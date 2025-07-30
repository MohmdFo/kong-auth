#!/usr/bin/env python3
"""
Test Runner for Kong Auth Service
Run all tests or specific test modules
"""

import sys
import os
import subprocess
import argparse

def run_test_file(test_file):
    """Run a specific test file"""
    print(f"Running {test_file}...")
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False

def run_all_tests():
    """Run all test files"""
    test_files = [
        "test_api.py",
        "test_casdoor_auth.py", 
        "test_kong_api.py",
        "test_oidc_loading.py",
        "verify_casdoor_setup.py"
    ]
    
    print("Running Kong Auth Service Test Suite")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            success = run_test_file(test_file)
            if success:
                passed += 1
                print(f"✅ {test_file} - PASSED")
            else:
                failed += 1
                print(f"❌ {test_file} - FAILED")
        else:
            print(f"⚠️  {test_file} - NOT FOUND")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run Kong Auth Service tests")
    parser.add_argument("test_file", nargs="?", help="Specific test file to run")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.test_file:
        # Run specific test file
        if os.path.exists(args.test_file):
            success = run_test_file(args.test_file)
            sys.exit(0 if success else 1)
        else:
            print(f"Test file {args.test_file} not found")
            sys.exit(1)
    else:
        # Run all tests by default
        success = run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 