Quick Start Guide
================

Get Kong Auth Service running in 5 minutes!

Prerequisites
------------

Before you start, make sure you have:

* **Docker** installed and running
* **Docker Compose** installed
* **Git** installed
* **curl** (for testing) or any HTTP client

Step 1: Clone the Repository
---------------------------

.. code-block:: bash

   git clone <repository-url>
   cd kong-auth

Step 2: Start the Services
-------------------------

.. code-block:: bash

   # Start all services with Docker Compose
   make quick-dev

This command will:
- Start Kong Gateway on port 8005
- Start Kong Admin API on port 8006
- Start Auth Service on port 8000
- Start Sample Service on port 8001
- Configure all services automatically

Step 3: Create Your First User
-----------------------------

.. code-block:: bash

   # Create a new user (consumer)
   curl -X POST "http://localhost:8000/create-consumer" \
     -H "Content-Type: application/json" \
     -d '{"username": "myuser"}'

You should get a response like:

.. code-block:: json

   {
     "consumer_id": "12345678-1234-1234-1234-123456789012",
     "username": "myuser",
     "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "secret": "base64_encoded_secret_here"
   }

**Save the JWT token** - you'll need it for the next step!

Step 4: Test Authentication
---------------------------

.. code-block:: bash

   # Test access to protected endpoint
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8005/sample/status

Replace `YOUR_JWT_TOKEN` with the token from the previous step.

You should get a response like:

.. code-block:: json

   {
     "status": "ok",
     "message": "Sample service is running",
     "user": "myuser",
     "timestamp": "2024-01-15T10:30:00Z"
   }

Step 5: Explore More Endpoints
-----------------------------

.. code-block:: bash

   # Get user information
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8005/sample/user-info

   # Test protected data endpoint
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8005/sample/data

   # Try without token (should fail)
   curl http://localhost:8005/sample/status

What Just Happened?
-------------------

1. **Kong Gateway** started and is listening on port 8005
2. **Auth Service** created a new user account in Kong
3. **JWT Token** was generated and signed with a unique secret
4. **Protected Endpoint** validated your token and allowed access
5. **Sample Service** processed your request and returned data

Understanding the Flow
---------------------

.. image:: ../_static/images/quick-start-flow.png
   :alt: Quick Start Flow
   :align: center

1. **User Creation**: Auth Service creates a "consumer" in Kong
2. **Token Generation**: Auth Service creates a JWT token for the user
3. **Request**: User sends request with JWT token to Kong Gateway
4. **Validation**: Kong validates the token using the JWT plugin
5. **Routing**: If valid, Kong forwards request to Sample Service
6. **Response**: Sample Service responds with user-specific data

Key Components
--------------

**Port 8005 - Kong Gateway**
- Main entry point for all protected requests
- Validates JWT tokens before allowing access

**Port 8000 - Auth Service**
- Creates users and generates JWT tokens
- Manages user credentials

**Port 8001 - Sample Service**
- Example backend service
- Shows how protected services work

**Port 8006 - Kong Admin API**
- Management interface for Kong
- Used internally by Auth Service

Next Steps
----------

Now that you have Kong Auth Service running, you can:

1. **Read the Concepts**: Understand :doc:`../concepts/jwt-authentication` and :doc:`../concepts/kong-gateway`
2. **Explore the API**: Check out :doc:`../api/endpoints` for all available endpoints
3. **Customize Configuration**: Learn about :doc:`configuration` options
4. **Deploy to Production**: Follow :doc:`../deployment/production` guide

Troubleshooting
--------------

**Service won't start**
- Check if Docker is running
- Ensure ports 8000, 8001, 8005, 8006 are available
- Check Docker logs: `docker-compose logs`

**"Connection refused" errors**
- Wait a few seconds for services to start
- Check service health: `docker-compose ps`
- Verify all containers are running

**"401 Unauthorized" errors**
- Check that you're using the correct JWT token
- Ensure token is in the format: `Authorization: Bearer <token>`
- Verify token hasn't expired

**"CORS error" in browser**
- This is normal for direct API calls
- Use a tool like curl or Postman for testing
- CORS is configured for web applications

Need Help?
----------

If you encounter issues:

1. Check the :doc:`../troubleshooting` guide
2. Review the :doc:`../faq` for common questions
3. Check service logs: `docker-compose logs <service-name>`
4. Verify your setup matches the prerequisites

Congratulations! 🎉

You've successfully set up Kong Auth Service and tested JWT authentication. You now have a working authentication system that can protect any API or service. 