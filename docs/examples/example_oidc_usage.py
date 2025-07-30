#!/usr/bin/env python3
"""
Example OIDC Authentication Usage
This script demonstrates how to use the Casdoor OIDC authentication
with proper resource ownership enforcement
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_oidc_authentication():
    """Test OIDC authentication flow"""
    print("=== OIDC Authentication Test ===")
    
    # This would be the token obtained from Casdoor after OIDC login
    # In a real application, the frontend would:
    # 1. Redirect user to Casdoor for login
    # 2. Get authorization code
    # 3. Exchange code for tokens
    # 4. Use access token in API calls
    
    print("To test OIDC authentication:")
    print("1. Login to your Casdoor instance")
    print("2. Get the access token from your profile")
    print("3. Use it in the API calls below")
    print()

def test_user_info(token):
    """Test getting current user information"""
    print("=== Testing User Info ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"GET /me - Status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ User authenticated successfully!")
            print(f"   User ID: {user_info.get('id')}")
            print(f"   Username: {user_info.get('name')}")
            print(f"   Display Name: {user_info.get('display_name')}")
            print(f"   Email: {user_info.get('email')}")
            print(f"   Roles: {user_info.get('roles')}")
            print(f"   Permissions: {user_info.get('permissions')}")
            print(f"   OIDC Subject: {user_info.get('sub')}")
            return user_info
        else:
            print(f"❌ Failed to get user info: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_consumer_creation(token, username):
    """Test creating a consumer with ownership enforcement"""
    print(f"\n=== Testing Consumer Creation for {username} ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    consumer_data = {"username": username}
    
    try:
        response = requests.post(f"{BASE_URL}/create-consumer", 
                               headers=headers, 
                               json=consumer_data)
        print(f"POST /create-consumer - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Consumer created successfully!")
            print(f"   Username: {result.get('username')}")
            print(f"   Consumer UUID: {result.get('consumer_uuid')}")
            return result
        elif response.status_code == 403:
            print("❌ Access denied - You can only create consumers with your own username")
            return None
        else:
            print(f"❌ Failed to create consumer: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_resource_ownership(token, username):
    """Test resource ownership enforcement"""
    print(f"\n=== Testing Resource Ownership for {username} ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test getting consumer info
    try:
        response = requests.get(f"{BASE_URL}/consumers/{username}", headers=headers)
        print(f"GET /consumers/{username} - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully accessed own consumer")
        elif response.status_code == 403:
            print("❌ Access denied - Resource ownership check failed")
        elif response.status_code == 404:
            print("⚠️  Consumer not found")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test getting tokens
    try:
        response = requests.get(f"{BASE_URL}/consumers/{username}/tokens", headers=headers)
        print(f"GET /consumers/{username}/tokens - Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            print(f"✅ Successfully accessed own tokens ({len(tokens)} tokens)")
        elif response.status_code == 403:
            print("❌ Access denied - Resource ownership check failed")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_unauthorized_access(token, other_username):
    """Test that users cannot access other users' resources"""
    print(f"\n=== Testing Unauthorized Access to {other_username}'s Resources ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try to access another user's consumer
    try:
        response = requests.get(f"{BASE_URL}/consumers/{other_username}", headers=headers)
        print(f"GET /consumers/{other_username} - Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ Correctly denied access to another user's consumer")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Try to create a consumer for another user
    try:
        consumer_data = {"username": other_username}
        response = requests.post(f"{BASE_URL}/create-consumer", 
                               headers=headers, 
                               json=consumer_data)
        print(f"POST /create-consumer for {other_username} - Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ Correctly denied creating consumer for another user")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_admin_access(token):
    """Test admin user access (if user has admin role)"""
    print(f"\n=== Testing Admin Access ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test listing all consumers (admin function)
    try:
        response = requests.get(f"{BASE_URL}/consumers", headers=headers)
        print(f"GET /consumers - Status: {response.status_code}")
        
        if response.status_code == 200:
            consumers = response.json()
            print(f"✅ Admin access granted - Retrieved {len(consumers)} consumers")
        elif response.status_code == 403:
            print("❌ Access denied - User does not have admin privileges")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main test function"""
    print("Casdoor OIDC Authentication Example")
    print("=" * 50)
    
    # Show OIDC flow information
    test_oidc_authentication()
    
    # Test with token if provided
    if len(sys.argv) > 1:
        token = sys.argv[1]
        
        # Get user info
        user_info = test_user_info(token)
        
        if user_info:
            username = user_info.get('name', 'test_user')
            
            # Test consumer creation
            consumer_result = test_consumer_creation(token, username)
            
            # Test resource ownership
            test_resource_ownership(token, username)
            
            # Test unauthorized access
            test_unauthorized_access(token, "other_user")
            
            # Test admin access
            test_admin_access(token)
            
    else:
        print("To test with a token:")
        print(f"python {sys.argv[0]} <your_casdoor_access_token>")
        print()
        print("Example usage:")
        print("1. Login to Casdoor and get your access token")
        print("2. Run: python example_oidc_usage.py YOUR_TOKEN")
        print("3. The script will test various authentication scenarios")

if __name__ == "__main__":
    main() 