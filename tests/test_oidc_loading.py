#!/usr/bin/env python3
"""
Test OIDC Module Loading
This test verifies that the OIDC authentication module loads correctly
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_oidc_module_loading():
    """Test that the OIDC module can be imported and initialized"""
    try:
        from app.casdoor_oidc import CasdoorUser, casdoor_oidc, get_current_user

        print("✅ OIDC module imported successfully")

        # Check if Casdoor SDK was initialized
        if casdoor_oidc.casdoor:
            print("✅ Casdoor SDK initialized successfully")
        else:
            print("⚠️  Casdoor SDK not available (using fallback mode)")

        # Check configuration
        print(f"✅ Endpoint: {casdoor_oidc.endpoint}")
        print(f"✅ Client ID: {casdoor_oidc.client_id}")
        print(f"✅ Organization: {casdoor_oidc.organization}")
        print(f"✅ Application: {casdoor_oidc.application}")

        return True

    except ImportError as e:
        print(f"❌ Failed to import OIDC module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error initializing OIDC module: {e}")
        return False


def test_casdoor_user_class():
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
            "permissions": ["read"],
        }

        token_claims = {
            "sub": "built-in/testuser",
            "iss": "https://iam.ai-lab.ir",
            "aud": "f83fb202807419aee818",
            "exp": 1234567890,
            "iat": 1234567890,
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
        print(f"❌ Error testing CasdoorUser class: {e}")
        return False


def test_certificate_loading():
    """Test certificate loading functionality"""
    try:
        from app.casdoor_oidc import casdoor_oidc

        # Test certificate loading
        cert_path = "casdoor_cert.pem"
        if os.path.exists(cert_path):
            cert_content = casdoor_oidc._load_certificate_key()
            if cert_content:
                print("✅ Certificate loaded successfully")
                return True
            else:
                print("⚠️  Certificate file exists but is empty")
                return False
        else:
            print("⚠️  Certificate file not found (this is expected if not configured)")
            return True

    except Exception as e:
        print(f"❌ Error testing certificate loading: {e}")
        return False


def main():
    """Run all OIDC tests"""
    print("Testing OIDC Module Loading")
    print("=" * 40)

    tests = [
        ("Module Loading", test_oidc_module_loading),
        ("User Class", test_casdoor_user_class),
        ("Certificate Loading", test_certificate_loading),
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
        print("🎉 All OIDC tests passed!")
        return 0
    else:
        print("💥 Some OIDC tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
