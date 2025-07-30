#!/usr/bin/env python3
"""
Verify Casdoor Setup
This script verifies that the Casdoor configuration is correct
"""

import os
import sys
from dotenv import load_dotenv

def check_env_variables():
    """Check if all required environment variables are set"""
    print("=== Checking Environment Variables ===")
    
    required_vars = [
        "CASDOOR_ENDPOINT",
        "CASDOOR_CLIENT_ID", 
        "CASDOOR_CLIENT_SECRET",
        "CASDOOR_ORG_NAME",
        "CASDOOR_APP_NAME"
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:10]}..." if len(value) > 10 else f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_good = False
    
    return all_good

def check_certificate_file():
    """Check if the certificate file exists and is readable"""
    print("\n=== Checking Certificate File ===")
    
    cert_path = "casdoor_cert.pem"
    
    if not os.path.exists(cert_path):
        print(f"❌ Certificate file '{cert_path}' not found")
        return False
    
    try:
        with open(cert_path, 'r') as f:
            content = f.read()
            if "-----BEGIN PUBLIC KEY-----" in content or "-----BEGIN CERTIFICATE-----" in content:
                print(f"✅ Certificate file '{cert_path}' found and appears valid")
                print(f"   File size: {len(content)} characters")
                return True
            else:
                print(f"⚠️  Certificate file '{cert_path}' found but content doesn't look like a valid certificate")
                return False
    except Exception as e:
        print(f"❌ Error reading certificate file: {e}")
        return False

def test_casdoor_connection():
    """Test connection to Casdoor endpoint"""
    print("\n=== Testing Casdoor Connection ===")
    
    try:
        import httpx
        import asyncio
        
        async def test_connection():
            endpoint = os.getenv("CASDOOR_ENDPOINT")
            if not endpoint:
                print("❌ CASDOOR_ENDPOINT not set")
                return False
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{endpoint}/api/get-account", timeout=10.0)
                    if response.status_code == 401:
                        print(f"✅ Casdoor endpoint '{endpoint}' is reachable (401 expected without auth)")
                        return True
                    elif response.status_code == 200:
                        print(f"✅ Casdoor endpoint '{endpoint}' is reachable")
                        return True
                    else:
                        print(f"⚠️  Casdoor endpoint '{endpoint}' responded with status {response.status_code}")
                        return True  # Still reachable
            except httpx.ConnectError:
                print(f"❌ Cannot connect to Casdoor endpoint '{endpoint}'")
                return False
            except Exception as e:
                print(f"⚠️  Error testing Casdoor connection: {e}")
                return False
        
        return asyncio.run(test_connection())
        
    except ImportError:
        print("⚠️  httpx not available, skipping connection test")
        return True

def main():
    """Main verification function"""
    print("Casdoor Setup Verification")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    env_ok = check_env_variables()
    
    # Check certificate file
    cert_ok = check_certificate_file()
    
    # Test connection
    connection_ok = test_casdoor_connection()
    
    # Summary
    print("\n=== Summary ===")
    if env_ok and cert_ok and connection_ok:
        print("✅ All checks passed! Casdoor setup appears correct.")
        return 0
    else:
        print("❌ Some checks failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 