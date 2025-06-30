Kong Gateway and Plugins Explained
==================================

What is Kong Gateway?
---------------------

Kong Gateway is like a **smart security guard** that sits in front of your applications and APIs. Think of it as a bouncer at a club who checks everyone's ID before letting them in. Kong Gateway:

* **Protects** your services from unauthorized access
* **Routes** requests to the correct backend services
* **Validates** authentication tokens
* **Logs** all incoming requests
* **Scales** to handle thousands of requests per second

.. image:: ../_static/images/kong-gateway-overview.png
   :alt: Kong Gateway Overview
   :align: center

Why Do We Use Kong?
-------------------

Imagine you have a building with many rooms (your services), and you want to control who can enter each room. You could:

1. **Put a guard at each door** (security in each service) - Expensive and hard to manage
2. **Put one guard at the main entrance** (Kong Gateway) - Efficient and centralized

Kong Gateway is that main guard. It:
- **Centralizes security** - All authentication happens in one place
- **Reduces complexity** - Your services don't need to handle authentication
- **Improves performance** - Fast, optimized security checks
- **Provides flexibility** - Easy to add new security rules

Kong Architecture in Our System
-------------------------------

.. image:: ../_static/images/kong-architecture.png
   :alt: Kong Architecture
   :align: center

**Kong Gateway** (Port 8005)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- The main entry point for all protected requests
- Validates JWT tokens before allowing access
- Routes requests to the correct backend service

**Kong Admin API** (Port 8006)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Management interface for Kong
- Used to configure services, routes, and plugins
- Not accessible to end users (admin only)

**Backend Services**
^^^^^^^^^^^^^^^^^^^^
- Your actual applications (like the sample service)
- Only receive requests that have passed Kong's security checks
- Don't need to handle authentication themselves

The Two Essential Plugins
-------------------------

We use two main plugins in Kong to make our system work:

1. **JWT Plugin** - Handles authentication
2. **CORS Plugin** - Handles cross-origin requests

Let's understand each one in detail.

JWT Plugin - The Authentication Guardian
----------------------------------------

The JWT Plugin is like a **passport control officer** who checks every person's passport (JWT token) before allowing them to proceed.

.. image:: ../_static/images/jwt-plugin-flow.png
   :alt: JWT Plugin Flow
   :align: center

What Does the JWT Plugin Do?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Intercepts Requests**: Catches every request before it reaches your service
2. **Extracts Tokens**: Looks for JWT tokens in the request
3. **Validates Tokens**: Checks if the token is valid and not expired
4. **Grants/Denies Access**: Either allows the request through or blocks it

Our JWT Plugin Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "name": "jwt",
     "config": {
       "uri_param_names": ["jwt"],
       "cookie_names": ["jwt"],
       "key_claim_name": "iss",
       "secret_is_base64": true,
       "claims_to_verify": ["exp"],
       "anonymous": null,
       "run_on_preflight": true,
       "maximum_expiration": 31536000,
       "header_names": ["authorization"]
     }
   }

Let's break down each configuration option:

**uri_param_names: ["jwt"]**
- Allows tokens to be passed as URL parameters
- Example: `http://api.example.com/data?jwt=your_token_here`
- Useful for GET requests where headers might be limited

**cookie_names: ["jwt"]**
- Allows tokens to be passed as cookies
- Example: `Cookie: jwt=your_token_here`
- Useful for web applications that use cookies

**key_claim_name: "iss"**
- Tells Kong which field in the JWT token identifies the user
- In our tokens, the "iss" field contains the username
- Kong uses this to look up the user's secret key

**secret_is_base64: true**
- Tells Kong that the secret keys are encoded in base64 format
- This is how we store secrets in our system
- Kong will decode the base64 before using it to verify the token

**claims_to_verify: ["exp"]**
- Tells Kong which JWT claims to validate
- "exp" means "expiration time"
- Kong will check if the token has expired

**anonymous: null**
- Prevents anonymous access (no token = no access)
- If set to a consumer ID, that consumer would be used for requests without tokens

**run_on_preflight: true**
- Applies JWT validation to OPTIONS requests (CORS preflight)
- Ensures CORS requests are also authenticated

**maximum_expiration: 31536000**
- Maximum allowed token expiration time (1 year in seconds)
- Prevents tokens from being valid for too long
- Security measure against long-term token abuse

**header_names: ["authorization"]**
- Tells Kong where to look for the JWT token
- Standard format: `Authorization: Bearer your_token_here`

How JWT Plugin Validation Works
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Request Arrives**: User sends request with JWT token
2. **Token Extraction**: Kong extracts token from Authorization header
3. **Issuer Lookup**: Kong reads the "iss" field to identify the user
4. **Secret Retrieval**: Kong looks up the user's secret key
5. **Signature Verification**: Kong verifies the token's digital signature
6. **Expiration Check**: Kong checks if the token has expired
7. **Access Decision**: If all checks pass, request proceeds; otherwise, blocked

Real-World Analogy
^^^^^^^^^^^^^^^^^^

Think of the JWT Plugin like a **high-tech security scanner**:

* **Token = ID Card**: Contains your photo, name, and expiration date
* **Issuer (iss) = Your Name**: The scanner reads your name from the ID
* **Secret = Security Database**: The scanner looks up your record in a database
* **Signature = Hologram**: The scanner checks if the ID has a valid hologram
* **Expiration = Valid Date**: The scanner checks if your ID hasn't expired

CORS Plugin - The Cross-Origin Bridge
-------------------------------------

CORS stands for **Cross-Origin Resource Sharing**. Think of it as a **diplomatic passport** that allows requests from different websites to access your API.

.. image:: ../_static/images/cors-plugin-flow.png
   :alt: CORS Plugin Flow
   :align: center

What is CORS?
^^^^^^^^^^^^^

Imagine you have a website at `https://myapp.com` that wants to call an API at `https://api.example.com`. By default, web browsers block this because it's a "cross-origin" request (different domains). CORS tells the browser "it's okay, let this request through."

Our CORS Plugin Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {
     "name": "cors",
     "config": {
       "origins": ["*"],
       "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
       "headers": ["Content-Type", "Authorization"],
       "exposed_headers": ["X-Consumer-ID", "X-Consumer-Username"],
       "credentials": true,
       "max_age": 3600,
       "preflight_continue": false
     }
   }

Let's break down each configuration option:

**origins: ["*"]**
- Allows requests from any website
- "*" means "all origins are allowed"
- In production, you might restrict this to specific domains

**methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]**
- Specifies which HTTP methods are allowed
- OPTIONS is needed for CORS preflight requests
- Covers all common API operations

**headers: ["Content-Type", "Authorization"]**
- Allows these headers in requests
- "Content-Type" for JSON data
- "Authorization" for JWT tokens

**exposed_headers: ["X-Consumer-ID", "X-Consumer-Username"]**
- Headers that Kong adds to responses
- These headers contain user information
- Your frontend can read these headers

**credentials: true**
- Allows cookies and authentication headers
- Required for JWT token authentication
- Enables secure cross-origin requests

**max_age: 3600**
- How long browsers should cache CORS settings (1 hour)
- Reduces the number of preflight requests
- Improves performance

**preflight_continue: false**
- Stops preflight requests at Kong
- Kong handles the CORS response
- Backend services don't need to handle CORS

How CORS Plugin Works
^^^^^^^^^^^^^^^^^^^^^

1. **Preflight Request**: Browser sends OPTIONS request to check if cross-origin is allowed
2. **CORS Response**: Kong responds with allowed origins, methods, and headers
3. **Actual Request**: If preflight succeeds, browser sends the actual request
4. **Response Headers**: Kong adds CORS headers to the response

Real-World Analogy
^^^^^^^^^^^^^^^^^^

Think of CORS like **international travel rules**:

* **Origin = Country**: Where the request is coming from
* **Methods = Types of Visas**: What the visitor is allowed to do
* **Headers = Documents**: What documents the visitor can bring
* **Credentials = Diplomatic Status**: Whether the visitor has special privileges
* **Preflight = Visa Application**: Checking if the visit is allowed before traveling

Why Do We Need Both Plugins?
----------------------------

**JWT Plugin** ensures **security** (only authenticated users can access)
**CORS Plugin** ensures **accessibility** (web applications can use the API)

Together, they provide:
- ✅ **Secure API access** (JWT authentication)
- ✅ **Web application compatibility** (CORS support)
- ✅ **Flexible client support** (browsers, mobile apps, servers)
- ✅ **Centralized security management**

Plugin Interaction Flow
----------------------

.. image:: ../_static/images/plugin-interaction.png
   :alt: Plugin Interaction Flow
   :align: center

1. **Request Arrives**: User sends request from web browser
2. **CORS Preflight**: Browser sends OPTIONS request (handled by CORS plugin)
3. **JWT Validation**: If preflight passes, JWT plugin validates the token
4. **Request Processing**: If JWT is valid, request goes to backend service
5. **Response**: Service responds, Kong adds CORS headers, response sent to user

Common Scenarios
----------------

**Scenario 1: Valid JWT Token**
```
Request: GET /api/data (with valid JWT token)
Result: ✅ Access granted, data returned
```

**Scenario 2: Invalid JWT Token**
```
Request: GET /api/data (with invalid JWT token)
Result: ❌ Access denied, 401 Unauthorized
```

**Scenario 3: No JWT Token**
```
Request: GET /api/data (no token)
Result: ❌ Access denied, 401 Unauthorized
```

**Scenario 4: Cross-Origin Request**
```
Request: From https://myapp.com to https://api.example.com
Result: ✅ CORS headers added, request processed normally
```

Configuration Best Practices
---------------------------

1. **Security First**
   - Always use HTTPS in production
   - Restrict CORS origins to specific domains
   - Set reasonable token expiration times

2. **Performance Optimization**
   - Use appropriate max_age for CORS caching
   - Monitor Kong performance metrics
   - Scale Kong horizontally if needed

3. **Monitoring and Logging**
   - Enable Kong access logs
   - Monitor authentication failures
   - Track API usage patterns

4. **Error Handling**
   - Provide clear error messages
   - Log authentication failures for security analysis
   - Implement rate limiting for failed attempts

Troubleshooting Common Issues
-----------------------------

**Issue: "CORS error" in browser**
- Check CORS plugin configuration
- Verify origins include your frontend domain
- Ensure credentials: true is set

**Issue: "401 Unauthorized"**
- Check JWT token format
- Verify token hasn't expired
- Ensure secret key is correct

**Issue: "Invalid token"**
- Check token signature
- Verify issuer (iss) claim
- Ensure base64 encoding is correct

Next Steps
----------

Now that you understand Kong Gateway and its plugins, learn about:
- :doc:`../concepts/architecture` - How everything works together
- :doc:`../guides/configuration` - How to configure the system
- :doc:`../api/endpoints` - Available API endpoints 