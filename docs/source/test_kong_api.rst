Kong Management API Testing
===========================

Overview
--------

The Kong Management API includes a comprehensive test suite that validates all endpoints and functionality. The test suite is designed to work with both running and non-running Kong instances, providing helpful feedback and troubleshooting guidance.

Test Script
----------

The main test script is located at: ``test_kong_api.py``

This script provides:

* **Automated Testing**: Tests all API endpoints automatically
* **Error Handling**: Graceful handling of connection and validation errors
* **Troubleshooting**: Helpful guidance when tests fail
* **Status Reporting**: Clear pass/fail status for each test
* **Resource Cleanup**: Automatic cleanup of test resources

Test Categories
--------------

Kong Status Test
^^^^^^^^^^^^^^^

Tests the Kong status endpoint to verify connectivity:

.. code-block:: python

   async def test_kong_status(self):
       """Test Kong status endpoint"""
       status = await self._make_request("GET", "/kong/status")
       if status["status"] == "healthy":
           self.log_test("Kong Status", True, f"Status: {status['status']}")
           return True
       else:
           self.log_test("Kong Status", False, f"Kong unhealthy: {status.get('error', 'Unknown error')}")
           return False

Service Management Tests
^^^^^^^^^^^^^^^^^^^^^^^

Tests all service CRUD operations:

* **Create Service**: Validates service creation with various configurations
* **List Services**: Tests service listing with proper response format
* **Get Service**: Verifies individual service retrieval
* **Update Service**: Tests service update functionality
* **Delete Service**: Validates service deletion

Route Management Tests
^^^^^^^^^^^^^^^^^^^^^

Tests all route CRUD operations:

* **Create Route**: Validates route creation with different configurations
* **List Routes**: Tests route listing with optional service filtering
* **Get Route**: Verifies individual route retrieval
* **Update Route**: Tests route update functionality
* **Delete Route**: Validates route deletion

Plugin Management Tests
^^^^^^^^^^^^^^^^^^^^^^

Tests plugin operations:

* **Enable Plugin**: Tests plugin enabling with various configurations
* **List Plugins**: Tests plugin listing with optional service filtering
* **Delete Plugin**: Validates plugin deletion

Health and Monitoring Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^

Tests monitoring endpoints:

* **Service Health**: Tests service health endpoint
* **Complete Service Setup**: Tests one-shot service configuration

Running the Tests
----------------

Prerequisites
^^^^^^^^^^^^

1. **API Server**: Your Kong Auth Service must be running
2. **Kong Gateway**: Optional but recommended for full testing
3. **Python Dependencies**: Install required packages

Setup
^^^^^

.. code-block:: bash

   # Start Kong for testing (recommended)
   ./start-kong-for-testing.sh
   
   # Or manually start Kong
   docker-compose -f kong/docker-compose.kong.yml up -d
   
   # Start the API server
   python -m app.main

Execution
^^^^^^^^^

.. code-block:: bash

   # Run all tests
   python test_kong_api.py
   
   # Run with specific environment variables
   API_BASE_URL=http://localhost:8000 KONG_ADMIN_URL=http://localhost:8006 python test_kong_api.py

Test Output
----------

The test suite provides detailed output:

.. code-block:: text

   🧪 Running Kong Management API Tests
   ==================================================
   API Base URL: http://localhost:8000
   Kong Admin URL: http://localhost:8006
   ==================================================

   🔍 Running: Kong Status
   ✅ PASS Kong Status
      Status: healthy

   🔍 Running: Create Service
   ✅ PASS Create Service
      Service created: example-service

   🔍 Running: List Services
   ✅ PASS List Services
      Found 1 services

   📊 Test Summary
   ==================================================
   ✅ PASS Kong Status
      Status: healthy
   ✅ PASS Create Service
      Service created: example-service
   ✅ PASS List Services
      Found 1 services
   ✅ PASS Get Service
      Service retrieved: example-service
   ✅ PASS Create Route
      Route created: test-route
   ✅ PASS List Routes
      Found 1 routes
   ✅ PASS Enable Plugin
      Plugin enabled: cors
   ✅ PASS Service Health
      Health status: healthy
   ✅ PASS Complete Service Setup
      Complete service setup successful
   ✅ PASS Cleanup
      Test resources cleaned up

   📈 Results: 10/10 tests passed
   🎉 All tests passed!

Error Handling
-------------

The test suite handles various error scenarios:

Connection Errors
^^^^^^^^^^^^^^^^

When Kong is not accessible:

.. code-block:: text

   ❌ FAIL Create Service
      Kong Admin API not accessible - Kong may not be running

   🔧 Troubleshooting
   ================================================================
   If tests are failing due to connection errors, Kong may not be running.

   To start Kong for testing:
   1. Run: ./start-kong-for-testing.sh
   2. Or manually: docker-compose -f kong/docker-compose.kong.yml up -d
   3. Wait for Kong to be ready, then run tests again

   To check Kong status:
      curl http://localhost:8006/status

Validation Errors
^^^^^^^^^^^^^^^^

When request data is invalid:

.. code-block:: text

   ❌ FAIL Create Service
      HTTP 400: {"detail": "Invalid URL format"}

HTTP Status Codes
^^^^^^^^^^^^^^^^

The test suite handles different HTTP status codes:

* **200 OK**: Success
* **400 Bad Request**: Invalid request data
* **404 Not Found**: Resource not found
* **409 Conflict**: Resource already exists
* **503 Service Unavailable**: Kong Admin API not accessible
* **504 Gateway Timeout**: Kong Admin API timeout
* **500 Internal Server Error**: Server error

Test Configuration
-----------------

Environment Variables
^^^^^^^^^^^^^^^^^^^^

The test suite uses these environment variables:

* **API_BASE_URL**: Your API base URL (default: ``http://localhost:8000``)
* **KONG_ADMIN_URL**: Kong Admin API URL (default: ``http://localhost:8006``)

Test Data
^^^^^^^^^

The test suite creates these test resources:

* **Services**: ``test-service``, ``complete-test-service``
* **Routes**: ``test-route``, ``complete-test-route``
* **Plugins**: CORS plugin on test service

All test resources are automatically cleaned up after testing.

Customization
------------

Adding New Tests
^^^^^^^^^^^^^^^

To add new tests:

1. **Create Test Method**: Add a new async method to the KongAPITester class
2. **Implement Logic**: Add test logic with proper error handling
3. **Add to Test List**: Include the test in the tests list in run_all_tests()
4. **Update Cleanup**: Add cleanup logic if needed

Example:

.. code-block:: python

   async def test_custom_endpoint(self):
       """Test custom endpoint"""
       try:
           result = await self._make_request("GET", "/kong/custom")
           if result.get("status") == "ok":
               self.log_test("Custom Test", True, "Custom endpoint working")
               return True
           else:
               self.log_test("Custom Test", False, "Custom endpoint failed")
               return False
       except Exception as e:
           self.log_test("Custom Test", False, str(e))
           return False

Modifying Test Data
^^^^^^^^^^^^^^^^^^

To modify test data:

1. **Service Configuration**: Update service_data in test_create_service()
2. **Route Configuration**: Update route_data in test_create_route()
3. **Plugin Configuration**: Update plugin_data in test_enable_plugin()

Integration with CI/CD
---------------------

The test suite is designed for CI/CD integration:

Exit Codes
^^^^^^^^^^

* **0**: All tests passed
* **1**: Some tests failed

Environment Setup
^^^^^^^^^^^^^^^^

For CI/CD environments:

.. code-block:: yaml

   # Example GitHub Actions step
   - name: Test Kong Management API
     run: |
       # Start Kong
       docker-compose -f kong/docker-compose.kong.yml up -d
       
       # Wait for Kong to be ready
       sleep 10
       
       # Run tests
       python test_kong_api.py

Continuous Testing
^^^^^^^^^^^^^^^^

For continuous testing:

1. **Automated Setup**: Use scripts to start Kong automatically
2. **Health Checks**: Verify Kong is ready before testing
3. **Parallel Testing**: Run tests in parallel if needed
4. **Reporting**: Generate test reports for monitoring

Best Practices
-------------

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up test resources
3. **Error Handling**: Handle all potential errors gracefully
4. **Logging**: Provide clear error messages
5. **Documentation**: Document test purpose and expected behavior

Troubleshooting
--------------

Common Issues
^^^^^^^^^^^^

1. **Kong Not Running**: Start Kong before running tests
2. **API Server Not Running**: Ensure the API server is started
3. **Network Issues**: Check firewall and network connectivity
4. **Resource Conflicts**: Clean up existing resources manually

Debug Mode
^^^^^^^^^^

For debugging, modify the test script to add more logging:

.. code-block:: python

   # Add debug logging
   print(f"DEBUG: Making request to {url}")
   print(f"DEBUG: Request data: {kwargs}")
   print(f"DEBUG: Response: {response.text}")

Manual Testing
^^^^^^^^^^^^

For manual testing:

.. code-block:: bash

   # Test individual endpoints
   curl -X GET http://localhost:8000/kong/status
   curl -X POST http://localhost:8000/kong/services -H "Content-Type: application/json" -d '{"name":"test","url":"http://localhost:8001"}'

See Also
--------

* :doc:`kong-management-api` - Complete API reference
* :doc:`example_kong_api_usage` - Usage examples
* :doc:`../README` - Project overview and setup instructions 