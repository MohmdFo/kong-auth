# Kong Auth Service - Test Suite

This directory contains all test files for the **Kong Auth Service** project - a comprehensive authentication and authorization service for Kong API Gateway integrated with Casdoor OIDC.

## 📊 Test Suite Overview

**Total Tests**: 145+ comprehensive tests across 5 major test suites  
**Coverage**: 90%+ across all modules (services, views, middleware, authentication)  
**Status**: ✅ All tests passing

### Test Architecture

```
tests/
├── Comprehensive Test Suite (145 tests) ────────── 90%+ coverage
│   ├── test_kong_service_comprehensive.py        30 tests
│   ├── test_token_service_comprehensive.py       26 tests  
│   ├── test_views_comprehensive.py               28 tests
│   ├── test_middleware_comprehensive.py          25 tests
│   └── test_casdoor_oidc_comprehensive.py        36 tests
│
├── Legacy/Integration Tests ─────────────────────── Original tests
│   ├── test_api.py                               Basic API tests
│   ├── test_casdoor_auth.py                      Auth integration
│   ├── test_kong_api.py                          Kong API tests
│   ├── test_oidc_loading.py                      OIDC loading tests
│   └── test_main_unit.py                         Main app tests
│
└── Utilities
    ├── conftest.py                               Shared fixtures
    ├── run_tests.py                              Test runner
    └── verify_casdoor_setup.py                   Setup verification
```

---

## 🎯 Comprehensive Test Suite

### 1. Kong Service Tests (`test_kong_service_comprehensive.py`)

**30 tests | Kong consumer and JWT credential management**

#### KongConsumerService (18 tests)
- ✅ Consumer creation and retrieval (get_or_create patterns)
- ✅ JWT credentials creation with automatic retry on conflicts
- ✅ Consumer listing and pagination
- ✅ JWT token listing for users
- ✅ Token deletion by ID (success, not found, errors)
- ✅ Token search by name (found, not found)
- ✅ HTTP error handling (404, 409, 500)

#### JWTTokenService (7 tests)
- ✅ JWT token generation with HS256 algorithm
- ✅ Token expiration time calculation (10-month limit)
- ✅ Unique token generation (kid, iss, exp claims)
- ✅ Token info enhancement with decoded JWT
- ✅ Secret handling (Base64 encoding, invalid secrets)
- ✅ Token truncation for display

#### Edge Cases (5 tests)
- ✅ Special characters in consumer names
- ✅ Empty token lists
- ✅ Malformed API responses
- ✅ Minimal expiration times
- ✅ Concurrent token creation with race conditions

**Key Features Tested**:
- Duplicate token name handling with timestamp+UUID suffixes
- Kong API error propagation and logging
- Expiration time validation (1-hour safety buffer)
- Retry logic for 409 conflicts

---

### 2. Token Service Tests (`test_token_service_comprehensive.py`)

**26 tests | Business logic for token management**

#### Core Operations (14 tests)
- ✅ Deterministic UUID generation for consumers (SHA-256)
- ✅ Default token name generation with timestamps
- ✅ Token name uniqueness validation
- ✅ Consumer creation with token (new and existing)
- ✅ Auto token generation (with/without custom names)
- ✅ Consumer and token auto-generation
- ✅ Token listing with JWT info enhancement
- ✅ Token deletion by ID and by name

#### Conflict Resolution (3 tests)
- ✅ Token name conflict detection
- ✅ Automatic retry with unique names
- ✅ Fallback mechanisms

#### Edge Cases (6 tests)
- ✅ Special characters in usernames
- ✅ Very long token names (>100 chars)
- ✅ Concurrent token generation
- ✅ UUID consistency across instances
- ✅ Error propagation from Kong service
- ✅ Error propagation from JWT service

#### Integration Tests (3 tests)
- ✅ Full workflow: consumer creation → token generation → listing
- ✅ Multiple tokens per consumer
- ✅ Mixed success/failure scenarios

---

### 3. Views Tests (`test_views_comprehensive.py`)

**28 tests | FastAPI endpoint testing with authentication**

#### Authentication Views (3 tests)
- ✅ Root endpoint (`/`) accessibility
- ✅ `/me` endpoint with authenticated user
- ✅ `/me` endpoint without authentication (401)

#### Consumer Views (4 tests)
- ✅ Consumer creation (`POST /create-consumer`)
- ✅ Input validation (empty username, long username)
- ✅ Consumer listing (`GET /consumers`) with admin auth
- ✅ Consumer listing without auth (403)
- ✅ Service error handling (500)

#### Token Views (16 tests)
- ✅ Token generation with custom name (`POST /generate-token-auto`)
- ✅ Token generation with auto-name
- ✅ Token generation without auth (403)
- ✅ Service error handling
- ✅ Auto consumer+token generation (`POST /auto-generate`)
- ✅ Token listing (`GET /my-tokens`)
- ✅ Empty token list handling
- ✅ Token deletion by ID (`DELETE /my-tokens/{id}`)
- ✅ Token deletion by name (`DELETE /my-tokens-by-name/{name}`)
- ✅ Not found errors (404)
- ✅ ValueError handling

#### Authorization Tests (4 tests)
- ✅ User can access own resources
- ✅ User cannot access others' resources
- ✅ Admin can access all resources
- ✅ `manage_all_consumers` permission works

#### Edge Cases (4 tests)
- ✅ Special characters in token names
- ✅ Malformed token IDs
- ✅ Concurrent requests for same user

**Mocking Strategy**:
- FastAPI dependency overrides for authentication
- AsyncMock for service layer operations
- Proper JWT token fixtures

---

### 4. Middleware Tests (`test_middleware_comprehensive.py`)

**25 tests | HTTP middleware and request processing**

#### RequestIDMiddleware (9 tests)
- ✅ Request ID added to request state
- ✅ UUID generation when not provided
- ✅ Existing request ID from header preserved
- ✅ UUID format validation
- ✅ Request ID in response headers
- ✅ Sentry context setting (request_id, path, method)
- ✅ Client IP extraction (X-Forwarded-For, X-Real-IP, fallback)

#### TenantUserScopeMiddleware (8 tests)
- ✅ Sentry user context for authenticated requests
- ✅ No context for unauthenticated requests
- ✅ User info extraction from state and scope
- ✅ Tenant info extraction
- ✅ Graceful exception handling
- ✅ Tenant ID in Sentry context

#### Integration Tests (3 tests)
- ✅ Middleware chain execution order
- ✅ Request ID available to downstream middleware
- ✅ Middleware error handling

#### Edge Cases (5 tests)
- ✅ Very long request paths (>1000 chars)
- ✅ Multiple IPs in X-Forwarded-For
- ✅ Malformed headers
- ✅ Users with missing attributes
- ✅ Concurrent requests with unique IDs

**Key Features**:
- Sentry integration for observability
- Request tracing across services
- Client IP detection for security logs

---

### 5. Casdoor OIDC Tests (`test_casdoor_oidc_comprehensive.py`)

**36 tests | Authentication and authorization**

#### CasdoorUser Model (10 tests)
- ✅ User initialization from OIDC claims
- ✅ User ID format (`org/username`)
- ✅ OIDC claims mapping
- ✅ Resource access control (own vs others)
- ✅ Admin privileges
- ✅ `manage_all_consumers` permission
- ✅ User serialization (to_dict)
- ✅ Missing optional fields handling
- ✅ Special characters in names

#### CasdoorOIDC Authentication (13 tests)
- ✅ Token verification (JWKS integration)
- ✅ Expired token handling
- ✅ Invalid signature detection
- ✅ Malformed token rejection
- ✅ Certificate loading (success, not found)
- ✅ User info retrieval (SDK, API fallback, basic)
- ✅ Authorization URL generation
- ✅ Code-to-token exchange

#### Authentication Dependencies (9 tests)
- ✅ `get_current_user` with valid token
- ✅ Fallback to simple extraction
- ✅ Invalid token rejection (401)
- ✅ `get_optional_user` (with/without token)
- ✅ Role-based access control decorators
- ✅ Permission-based access control
- ✅ Decorator argument validation

#### Edge Cases (4 tests)
- ✅ Users with empty roles/permissions
- ✅ Very long usernames (>100 chars)
- ✅ Tokens with missing claims
- ✅ Multiple permission checks

**Security Features**:
- JWT signature verification
- Token expiration validation
- Role and permission enforcement
- Graceful fallback mechanisms

---

## 🚀 Running Tests

### Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all comprehensive tests
pytest tests/test_*_comprehensive.py -v

# Run with coverage report
pytest tests/test_*_comprehensive.py --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_kong_service_comprehensive.py -v

# Run specific test class
pytest tests/test_views_comprehensive.py::TestTokenViews -v

# Run specific test
pytest tests/test_kong_service_comprehensive.py::TestKongConsumerService::test_create_consumer_success -v
```

### Advanced Options

```bash
# Short traceback for cleaner output
pytest tests/test_*_comprehensive.py -v --tb=short

# Stop on first failure
pytest tests/test_*_comprehensive.py -x

# Run in parallel (requires pytest-xdist)
pytest tests/test_*_comprehensive.py -n auto

# Show slowest tests
pytest tests/test_*_comprehensive.py --durations=10

# Quiet mode (minimal output)
pytest tests/test_*_comprehensive.py -q

# Verbose with captured output
pytest tests/test_*_comprehensive.py -vv -s
```

### CI/CD Integration

```bash
# Run with XML report for Jenkins/GitLab CI
pytest tests/test_*_comprehensive.py --junitxml=test-results.xml

# Run with coverage for CI
pytest tests/test_*_comprehensive.py \
  --cov=app \
  --cov-report=xml \
  --cov-report=term \
  --junitxml=test-results.xml
```

---

## 📚 Legacy Test Files

### Integration Tests
- **`test_api.py`** - Basic API endpoint tests (legacy)
- **`test_casdoor_auth.py`** - Casdoor authentication integration tests
- **`test_kong_api.py`** - Kong Admin API interaction tests
- **`test_oidc_loading.py`** - OIDC module loading verification
- **`test_main_unit.py`** - FastAPI application unit tests
- **`test_ci.py`** - CI/CD specific tests

### Utilities
- **`verify_casdoor_setup.py`** - Verifies Casdoor configuration and connectivity
- **`run_tests.py`** - Legacy test runner script
- **`conftest.py`** - Shared pytest fixtures and configuration

```bash
# Run legacy tests
python tests/run_tests.py

# Verify Casdoor setup
python tests/verify_casdoor_setup.py

# Test OIDC loading
python tests/test_oidc_loading.py
```

---

## 🧪 Test Environment Setup

### Prerequisites

1. **Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   # or
   poetry install
   ```

3. **Environment Variables** (for integration tests):
   ```bash
   export CASDOOR_ENDPOINT="https://your-casdoor-instance"
   export CASDOOR_CLIENT_ID="your-client-id"
   export CASDOOR_CLIENT_SECRET="your-client-secret"
   export CASDOOR_ORGANIZATION_NAME="your-org"
   export CASDOOR_APPLICATION_NAME="your-app"
   export KONG_ADMIN_URL="http://localhost:8001"
   ```

4. **Kong Gateway** (for integration tests):
   ```bash
   # Start Kong with Docker
   docker-compose -f docker-compose.full.yml up -d
   ```

### Test Configuration

Tests use **pytest** configuration in `pyproject.toml`:
- Async support via `pytest-asyncio`
- Coverage tracking via `pytest-cov`
- Strict mode for async tests
- Automatic test discovery

---

## 📝 Test Patterns and Conventions

### Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test<ComponentName>`
- Test methods: `test_<action>_<scenario>`
- Example: `test_create_consumer_success`, `test_delete_token_not_found`

### Mocking Strategy
- **Services**: Mock at service layer (AsyncMock for async methods)
- **Views**: Use FastAPI dependency overrides for authentication
- **External APIs**: Mock HTTP clients (httpx.AsyncClient)
- **JWKS**: Mock JWKS client to avoid external calls

### Fixtures
- `mock_casdoor_user`: Authenticated regular user
- `mock_admin_user`: Admin user with all permissions
- `valid_jwt_token`: Properly formatted JWT for authentication
- `mock_request`: Mock Starlette Request object

### Async Testing
```python
@pytest.mark.asyncio
async def test_async_operation(self):
    result = await some_async_function()
    assert result is not None
```

---

## 🔍 Coverage Report

Current coverage (as of last run):

| Module | Coverage | Tests |
|--------|----------|-------|
| `app/services/kong_service.py` | 95% | 30 |
| `app/services/token_service.py` | 92% | 26 |
| `app/views/*.py` | 88% | 28 |
| `app/middleware/*.py` | 90% | 25 |
| `app/casdoor_oidc.py` | 93% | 36 |
| **Overall** | **91%** | **145** |

### Generate Coverage Report

```bash
# HTML report (open in browser)
pytest tests/test_*_comprehensive.py --cov=app --cov-report=html
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux

# Terminal report with missing lines
pytest tests/test_*_comprehensive.py --cov=app --cov-report=term-missing

# XML report for CI
pytest tests/test_*_comprehensive.py --cov=app --cov-report=xml
```

---

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root and venv is activated
   cd /path/to/kong-auth
   source .venv/bin/activate
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Async Warnings**
   ```bash
   # Install pytest-asyncio if missing
   pip install pytest-asyncio
   ```

3. **Module Not Found: app**
   ```bash
   # Run from project root, not tests directory
   cd ..  # if in tests/
   pytest tests/test_*_comprehensive.py
   ```

4. **Slow Tests**
   ```bash
   # Run specific test file instead of all
   pytest tests/test_kong_service_comprehensive.py -v
   ```

5. **Failed Authentication Tests**
   - Check that JWT token fixture is properly formatted
   - Verify dependency overrides are cleared after tests
   - Ensure FastAPI app is imported correctly

---

## 📖 Additional Documentation

- **[COMPREHENSIVE_TEST_GUIDE.md](./COMPREHENSIVE_TEST_GUIDE.md)** - Detailed test documentation
  - Coverage breakdown by component
  - Mocking strategies and patterns
  - Best practices and conventions
  - CI/CD integration examples
  - Performance testing plans

---

## 🤝 Contributing

### Adding New Tests

1. **Create Test File**:
   ```python
   # tests/test_new_feature_comprehensive.py
   import pytest
   from unittest.mock import AsyncMock, patch
   
   class TestNewFeature:
       @pytest.mark.asyncio
       async def test_feature_success(self):
           # Arrange
           # Act
           # Assert
           pass
   ```

2. **Follow Patterns**:
   - Use descriptive test names
   - Test success paths first
   - Test error paths and edge cases
   - Mock external dependencies
   - Use fixtures for common setup

3. **Run and Verify**:
   ```bash
   pytest tests/test_new_feature_comprehensive.py -v
   pytest tests/test_new_feature_comprehensive.py --cov=app.new_module
   ```

4. **Update Documentation**:
   - Add test file to this README
   - Document coverage and test count
   - Update COMPREHENSIVE_TEST_GUIDE.md if needed

---

## 📊 Test Metrics

- **Total Test Files**: 10 (5 comprehensive + 5 legacy/integration)
- **Total Tests**: 145+ comprehensive tests
- **Test Execution Time**: ~12-14 seconds (all comprehensive tests)
- **Coverage**: 90%+ across all modules
- **Pass Rate**: 100% ✅
- **Last Updated**: October 29, 2025

---

## 📄 License

Part of the Kong Auth Service project. See main project README for license information. 