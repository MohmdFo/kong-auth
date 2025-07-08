Welcome to Kong Auth Service Documentation
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   concepts/jwt-authentication
   concepts/kong-gateway
   concepts/architecture
   guides/quick-start
   api/endpoints
   kong-management-api
   example_kong_api_usage
   test_kong_api
   faq

.. image:: _static/images/architecture-overview.png
   :alt: Kong Auth Service Architecture
   :align: center

What is Kong Auth Service?
--------------------------

Kong Auth Service is a comprehensive authentication solution that combines the power of Kong Gateway with JWT (JSON Web Token) authentication. It provides a secure, scalable way to manage user access to your applications and APIs.

Key Features
^^^^^^^^^^^^

* **JWT Token Generation**: Automatically creates secure JWT tokens for users
* **Kong Integration**: Seamlessly works with Kong Gateway for API protection
* **Consumer Management**: Easy user and consumer management
* **Kong Management API**: Complete REST API for managing Kong services and routes
* **Dynamic Service Management**: Create and configure services without direct Kong access
* **Plugin Management**: Enable and configure Kong plugins through API
* **Scalable Architecture**: Built for high-traffic applications
* **Docker Ready**: Complete containerization support
* **Comprehensive Testing**: Built-in testing and validation tools

Who is this for?
^^^^^^^^^^^^^^^^

* **Developers** who need secure API authentication
* **DevOps Engineers** managing API gateways
* **System Administrators** implementing security policies
* **Business Users** who need to understand authentication flows
* **Anyone** who wants to learn about modern API security

Quick Start
----------

.. code-block:: bash

   # Clone the repository
   git clone <repository-url>
   cd kong-auth

   # Start with Docker
   make quick-dev

   # Create a user and get JWT token
   curl -X POST "http://localhost:8000/create-consumer" \
     -H "Content-Type: application/json" \
     -d '{"username": "myuser"}'

   # Use the token to access protected endpoints
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8005/sample/status

For detailed instructions, see :doc:`guides/quick-start`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 