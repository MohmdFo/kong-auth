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
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True

    def start_auth_service(self):
        """Start the FastAPI auth service"""
        print("🚀 Starting Auth Service...")
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
            print("✅ Auth Service started")
            return True
        except Exception as e:
            print(f"❌ Failed to start Auth Service: {e}")
            return False
    
    def start_sample_service(self):
        """Start the sample service"""
        print("🚀 Starting Sample Service...")
        try:
            process = subprocess.Popen(
                [sys.executable, "sample-service.py"],
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(("Sample Service", process))
            print("✅ Sample Service started")
            return True
        except Exception as e:
            print(f"❌ Failed to start Sample Service: {e}")
            return False
    
    async def setup_kong(self):
        """Set up Kong configuration"""
        print("🚀 Setting up Kong...")
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "setup-kong.py",
                cwd=Path(__file__).parent,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                print("✅ Kong setup completed")
                return True
            else:
                print(f"❌ Kong setup failed: {stderr.decode()}")
                return False
        except Exception as e:
            print(f"❌ Failed to setup Kong: {e}")
            return False

    async def wait_for_services(self):
        """Wait for services to be ready"""
        print("⏳ Waiting for services to be ready...")

        import httpx

        # Wait for auth service
        for i in range(30):  # Wait up to 30 seconds
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8000/", timeout=1.0)
                    if response.status_code == 200:
                        print("✅ Auth Service is ready")
                        break
            except:
                pass
            await asyncio.sleep(1)
        else:
            print("❌ Auth Service failed to start")
            return False

        # Wait for sample service
        for i in range(30):  # Wait up to 30 seconds
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8001/", timeout=1.0)
                    if response.status_code == 200:
                        print("✅ Sample Service is ready")
                        break
            except:
                pass
            await asyncio.sleep(1)
        else:
            print("❌ Sample Service failed to start")
            return False

        return True

    def stop_all(self):
        """Stop all running processes"""
        print("\n🛑 Stopping all services...")
        self.running = False

        for name, process in self.processes:
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️  {name} didn't stop gracefully, killing...")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}, shutting down...")
        self.stop_all()
        sys.exit(0)

    async def run(self):
        """Run all services"""
        print("🎯 Starting Kong Auth Test Environment")
        print("=" * 50)
        
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

            print("\n" + "=" * 50)
            print("✅ All services are running!")
            print("\n📋 Available endpoints:")
            print("  Auth Service:     http://localhost:8000")
            print("  Sample Service:   http://localhost:8001")
            print("  Kong Gateway:     http://localhost:8000")
            print("  Kong Admin:       http://localhost:8006")
            print("\n🔐 Protected endpoints (require JWT):")
            print("  GET/POST  http://localhost:8000/sample")
            print("  GET/POST  http://localhost:8000/sample/api")
            print("  GET       http://localhost:8000/sample/status")
            print("\n🧪 Test the complete flow:")
            print("  python test-complete-flow.py")
            print("\n📝 Manual testing:")
            print("  1. Create consumer: curl -X POST http://localhost:8000/create-consumer -H 'Content-Type: application/json' -d '{\"username\": \"testuser\"}'")
            print("  2. Use token: curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/sample/status")
            print("\nPress Ctrl+C to stop all services")
            print("=" * 50)

            # Keep running until interrupted
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n📡 Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.stop_all()

        return True

async def main():
    """Main function"""
    manager = ServiceManager()
    await manager.run()

if __name__ == "__main__":
    asyncio.run(main()) 