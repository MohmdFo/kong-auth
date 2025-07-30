# Tests Directory

This directory contains all test files for the Kong Auth Service.

## Test Files

### Core Tests
- **`test_api.py`** - Basic API endpoint tests
- **`test_casdoor_auth.py`** - Casdoor authentication tests
- **`test_kong_api.py`** - Kong management API tests
- **`test_oidc_loading.py`** - OIDC module loading and functionality tests

### Setup Verification
- **`verify_casdoor_setup.py`** - Verifies Casdoor configuration and connectivity

### Test Runner
- **`run_tests.py`** - Test runner script to execute all tests

## Running Tests

### Run All Tests
```bash
# From project root
python tests/run_tests.py

# Or from tests directory
cd tests
python run_tests.py
```

### Run Specific Test
```bash
# Run specific test file
python tests/run_tests.py test_casdoor_auth.py

# Or run directly
python tests/test_casdoor_auth.py
```

### Verify Setup
```bash
# Verify Casdoor configuration
python tests/verify_casdoor_setup.py

# Test OIDC module loading
python tests/test_oidc_loading.py
```

## Test Categories

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Fast execution

### Integration Tests
- Test API endpoints
- Test with real Kong instance
- Test Casdoor integration

### Setup Tests
- Verify configuration
- Check connectivity
- Validate dependencies

## Test Environment

Tests require:
- Kong Gateway running (for integration tests)
- Casdoor instance accessible
- Proper environment variables set
- Certificate file present

## Adding New Tests

1. Create test file with `test_` prefix
2. Follow pytest conventions
3. Add to `run_tests.py` if needed
4. Document test purpose in this README 