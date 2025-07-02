#!/usr/bin/env python3
"""
Start All Services Script
Starts the auth service, sample service, and sets up Kong automatically
"""

import asyncio
import subprocess
import time
import sys
import os
import signal
import threading
import logging
from pathlib import Path

# Add parent directory to path to import logging_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.logging_config import setup_logging

# Setup logging
logger = setup_logging()

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True

    def start_auth_service(self):
        """Start the FastAPI auth service"""
        logger.info("🚀 Starting Auth Service...")
        try:
            # Change to parent directory to run the auth service
            parent_dir = Path(__file__).parent.parent
            process = subprocess.Popen(
                [sys.executable, "run.py"],
                cwd=parent_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(("Auth Service", process))
            logger.info("✅ Auth Service started")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start Auth Service: {e}")
            return False
    
    def start_sample_service(self):
        """Start the sample service"""
        logger.info("🚀 Starting Sample Service...")
        try:
            process = subprocess.Popen(
                [sys.executable, "sample-service.py"],
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(("Sample Service", process))
            logger.info("✅ Sample Service started")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start Sample Service: {e}")
            return False
    
    async def setup_kong(self):
        """Set up Kong configuration"""
        logger.info("🚀 Setting up Kong...")
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "setup-kong.py",
                cwd=Path(__file__).parent,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info("✅ Kong setup completed")
                return True
            else:
                logger.error(f"❌ Kong setup failed: {stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to setup Kong: {e}")
            return False

    async def wait_for_services(self):
        """Wait for services to be ready"""
        logger.info("⏳ Waiting for services to be ready...")

        import httpx

        # Wait for auth service
        for i in range(30):  # Wait up to 30 seconds
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8000/", timeout=1.0)
                    if response.status_code == 200:
                        logger.info("✅ Auth Service is ready")
                        break
            except:
                pass
            await asyncio.sleep(1)
        else:
            logger.error("❌ Auth Service failed to start")
            return False

        # Wait for sample service
        for i in range(30):  # Wait up to 30 seconds
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8001/", timeout=1.0)
                    if response.status_code == 200:
                        logger.info("✅ Sample Service is ready")
                        break
            except:
                pass
            await asyncio.sleep(1)
        else:
            logger.error("❌ Sample Service failed to start")
            return False

        return True

    def stop_all(self):
        """Stop all running processes"""
        logger.info("🛑 Stopping all services...")
        self.running = False

        for name, process in self.processes:
            try:
                logger.info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  {name} didn't stop gracefully, killing...")
                process.kill()
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, shutting down...")
        self.stop_all()
        sys.exit(0)

    async def run(self):
        """Run all services"""
        logger.info("🎯 Starting Kong Auth Test Environment")
        logger.info("=" * 50)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            # Start services
            if not self.start_auth_service():
                return False

            if not self.start_sample_service():
                return False

            # Wait for services to be ready
            if not await self.wait_for_services():
                return False

            # Set up Kong
            if not await self.setup_kong():
                return False

            logger.info("=" * 50)
            logger.info("✅ All services are running!")
            logger.info("📋 Available endpoints:")
            logger.info("  Auth Service:     http://localhost:8000")
            logger.info("  Sample Service:   http://localhost:8001")
            logger.info("  Kong Gateway:     http://localhost:8000")
            logger.info("  Kong Admin:       http://localhost:8006")
            logger.info("🔐 Protected endpoints (require JWT):")
            logger.info("  GET/POST  http://localhost:8000/sample")
            logger.info("  GET/POST  http://localhost:8000/sample/api")
            logger.info("  GET       http://localhost:8000/sample/status")
            logger.info("🧪 Test the complete flow:")
            logger.info("  python test-complete-flow.py")
            logger.info("📝 Manual testing:")
            logger.info("  1. Create consumer: curl -X POST http://localhost:8000/create-consumer -H 'Content-Type: application/json' -d '{\"username\": \"testuser\"}'")
            logger.info("  2. Use token: curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/sample/status")
            logger.info("Press Ctrl+C to stop all services")
            logger.info("=" * 50)

            # Keep running until interrupted
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("📡 Interrupted by user")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        finally:
            self.stop_all()

        return True

async def main():
    """Main function"""
    manager = ServiceManager()
    await manager.run()

if __name__ == "__main__":
    asyncio.run(main()) 