#!/usr/bin/env python3
"""
CI Test Suite
This test runs in GitLab CI environment without external dependencies
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.main import app
        print("✅ Main application imports successfully")
        
        from app.casdoor_oidc import CasdoorUser, casdoor_oidc
        print("✅ OIDC module imports successfully")
        
        from app.kong_api import router
        print("✅ Kong API module imports successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    try:
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Check required environment variables
        required_vars = [
            "CASDOOR_ENDPOINT",
            "CASDOOR_CLIENT_ID", 
            "CASDOOR_CLIENT_SECRET",
            "CASDOOR_ORG_NAME",
            "CASDOOR_APP_NAME"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
            print("   This is expected in CI environment")
        else:
            print("✅ All environment variables are set")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_user_class():
    """Test CasdoorUser class functionality"""
    try:
        from app.casdoor_oidc import CasdoorUser
        
        # Test user creation
        user_data = {
            "owner": "built-in",
            "name": "testuser",
            "displayName": "Test User",
            "email": "test@example.com",
            "roles": ["user"],
            "permissions": ["read"]
        }
        
        token_claims = {
            "sub": "built-in/testuser",
            "iss": "https://iam.ai-lab.ir",
            "aud": "f83fb202807419aee818",
            "exp": 1234567890,
            "iat": 1234567890
        }
        
        user = CasdoorUser(user_data, token_claims)
        
        # Test basic properties
        assert user.name == "testuser"
        assert user.display_name == "Test User"
        assert user.email == "test@example.com"
        assert "user" in user.roles
        
        # Test resource access
        assert user.can_access_resource("testuser") == True
        assert user.can_access_resource("otheruser") == False
        
        print("✅ CasdoorUser class works correctly")
        return True
        
    except Exception as e:
        print(f"❌ User class test failed: {e}")
        return False

def test_project_structure():
    """Test that project structure is correct"""
    try:
        required_dirs = ["app", "docs", "tests"]
        required_files = [
            "app/main.py",
            "app/casdoor_oidc.py",
            "tests/run_tests.py",
            "docs/OIDC_IMPLEMENTATION_GUIDE.md",
            "requirements.txt"
        ]
        
        # Check directories
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                print(f"❌ Required directory missing: {dir_name}")
                return False
            print(f"✅ Directory exists: {dir_name}")
        
        # Check files
        for file_name in required_files:
            if not os.path.exists(file_name):
                print(f"❌ Required file missing: {file_name}")
                return False
            print(f"✅ File exists: {file_name}")
        
        return True
    except Exception as e:
        print(f"❌ Project structure test failed: {e}")
        return False

def main():
    """Run all CI tests"""
    print("Running CI Test Suite")
    print("=" * 40)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("User Class", test_user_class)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All CI tests passed!")
        return 0
    else:
        print("💥 Some CI tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 