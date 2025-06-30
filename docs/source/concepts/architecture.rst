System Architecture Overview
============================

Understanding the Big Picture
-----------------------------

The Kong Auth Service is like a **secure office building** with multiple floors, security checkpoints, and different departments. Let's break down how everything works together.

.. image:: ../_static/images/system-architecture.png
   :alt: Complete System Architecture
   :align: center

The Building Analogy
-------------------

Think of our system as a **secure office building**:

* **Main Entrance (Kong Gateway)** - Security checkpoint where everyone must show ID
* **Reception Desk (Auth Service)** - Where visitors get their access badges
* **Office Floors (Backend Services)** - Where the actual work happens
* **Security Office (Kong Admin)** - Where security policies are managed
* **Visitor Badges (JWT Tokens)** - Digital passes that prove you belong

.. image:: ../_static/images/building-analogy.png
   :alt: Building Analogy
   :align: center

System Components
-----------------

1. **Kong Gateway** (Port 8005) - The Main Security Checkpoint
2. **Kong Admin API** (Port 8006) - Security Management Office
3. **Auth Service** (Port 8000) - Badge Issuing Desk
4. **Sample Service** (Port 8001) - Example Office Floor
5. **JWT Tokens** - Digital Access Badges
6. **Plugins** - Security Rules and Policies

Let's explore each component in detail.

Component 1: Kong Gateway - The Main Security Checkpoint
--------------------------------------------------------

.. image:: ../_static/images/kong-gateway-detail.png
   :alt: Kong Gateway Detail
   :align: center

**What it does:**
- Acts as the main entrance to all protected services
- Validates JWT tokens before allowing access
- Routes requests to the correct backend service
- Logs all incoming and outgoing traffic

**How it works:**
1. **Request Arrives**: User sends request with JWT token
2. **Token Validation**: Kong checks if the token is valid
3. **Routing**: If valid, Kong forwards request to the correct service
4. **Response**: Service responds, Kong adds security headers, sends back to user

**Real-world analogy:**
Think of Kong Gateway as a **high-tech security guard** at the building entrance who:
- Checks everyone's ID badge (JWT token)
- Has a list of who's allowed where (routing rules)
- Logs everyone who enters and exits (access logs)
- Can deny entry to unauthorized people (401 errors)

Component 2: Kong Admin API - Security Management Office
--------------------------------------------------------

.. image:: ../_static/images/kong-admin-detail.png
   :alt: Kong Admin API Detail
   :align: center

**What it does:**
- Provides management interface for Kong Gateway
- Allows configuration of services, routes, and plugins
- Manages user accounts (consumers) and their credentials
- Not accessible to end users (admin only)

**How it works:**
1. **Configuration**: Admin sends configuration commands
2. **Validation**: Kong validates the configuration
3. **Application**: Kong applies the changes
4. **Confirmation**: Kong confirms the changes were applied

**Real-world analogy:**
Think of Kong Admin API as the **security management office** where:
- Security policies are created and updated
- Access lists are maintained
- Security rules are configured
- Only authorized personnel can access

Component 3: Auth Service - Badge Issuing Desk
----------------------------------------------

.. image:: ../_static/images/auth-service-detail.png
   :alt: Auth Service Detail
   :align: center

**What it does:**
- Creates new user accounts (consumers) in Kong
- Generates JWT tokens for users
- Manages user credentials and secrets
- Provides user management endpoints

**How it works:**
1. **User Registration**: User provides username
2. **Consumer Creation**: Auth service creates consumer in Kong
3. **Secret Generation**: Auth service generates unique secret for user
4. **Token Creation**: Auth service creates JWT token with user info
5. **Response**: Auth service returns token to user

**Real-world analogy:**
Think of the Auth Service as the **badge issuing desk** where:
- New employees get their access badges
- Badges are programmed with the right permissions
- Each badge has a unique code (secret)
- Badges expire after a certain time

Component 4: Sample Service - Example Office Floor
--------------------------------------------------

.. image:: ../_static/images/sample-service-detail.png
   :alt: Sample Service Detail
   :align: center

**What it does:**
- Provides example endpoints for testing
- Demonstrates how protected services work
- Shows Kong header information
- Serves as a template for real services

**How it works:**
1. **Request Receipt**: Receives requests that passed Kong security
2. **Header Processing**: Reads Kong-added headers (user info)
3. **Business Logic**: Performs the actual work
4. **Response**: Returns data with user context

**Real-world analogy:**
Think of the Sample Service as an **example office floor** where:
- Employees do their actual work
- They can see who's accessing their area (Kong headers)
- They don't need to check IDs (Kong already did that)
- They focus on their specific tasks

Component 5: JWT Tokens - Digital Access Badges
-----------------------------------------------

.. image:: ../_static/images/jwt-token-detail.png
   :alt: JWT Token Detail
   :align: center

**What they are:**
- Digital credentials that prove user identity
- Contain user information and expiration time
- Signed with a secret key to prevent forgery
- Can be used multiple times until expiration

**How they work:**
1. **Creation**: Auth service creates token with user info
2. **Signing**: Token is signed with user's secret key
3. **Usage**: User includes token in requests
4. **Validation**: Kong verifies token signature and expiration

**Real-world analogy:**
Think of JWT tokens as **digital access badges** that:
- Contain your photo and name (user info)
- Have an expiration date (exp claim)
- Are impossible to forge (digital signature)
- Can be used to access multiple areas (different endpoints)

Component 6: Plugins - Security Rules and Policies
--------------------------------------------------

.. image:: ../_static/images/plugins-detail.png
   :alt: Plugins Detail
   :align: center

**JWT Plugin:**
- Validates JWT tokens
- Checks token expiration
- Verifies digital signatures
- Grants or denies access

**CORS Plugin:**
- Handles cross-origin requests
- Allows web applications to access the API
- Manages browser security policies
- Adds necessary headers to responses

**Real-world analogy:**
Think of plugins as **security policies** that:
- Define who can access what (JWT plugin)
- Handle special cases like international visitors (CORS plugin)
- Can be easily updated without changing the building (modular)
- Work together to provide comprehensive security

Data Flow - How Everything Works Together
-----------------------------------------

.. image:: ../_static/images/data-flow.png
   :alt: Complete Data Flow
   :align: center

**Step 1: User Registration**
1. User calls Auth Service: "I want to create an account"
2. Auth Service creates consumer in Kong Admin API
3. Auth Service generates secret and JWT token
4. Auth Service returns token to user

**Step 2: Accessing Protected Service**
1. User sends request with JWT token to Kong Gateway
2. Kong Gateway validates token using JWT plugin
3. If valid, Kong Gateway forwards request to backend service
4. Backend service processes request and responds
5. Kong Gateway adds CORS headers and returns response

**Step 3: Service Processing**
1. Backend service receives request (already validated by Kong)
2. Service can read user info from Kong headers
3. Service performs business logic
4. Service returns response with user context

Security Layers
---------------

.. image:: ../_static/images/security-layers.png
   :alt: Security Layers
   :align: center

**Layer 1: Network Security**
- HTTPS encryption for all communications
- Firewall rules and network isolation
- Docker container security

**Layer 2: Gateway Security**
- Kong Gateway as single entry point
- Request validation and filtering
- Rate limiting and DDoS protection

**Layer 3: Authentication Security**
- JWT token validation
- Digital signature verification
- Token expiration checking

**Layer 4: Application Security**
- Input validation and sanitization
- Output encoding and filtering
- Error handling and logging

**Layer 5: Data Security**
- Secure secret storage
- Base64 encoding for compatibility
- No sensitive data in tokens

Scalability and Performance
---------------------------

.. image:: ../_static/images/scalability.png
   :alt: Scalability Architecture
   :align: center

**Horizontal Scaling:**
- Multiple Kong Gateway instances
- Load balancer distributing traffic
- Shared configuration across instances

**Performance Optimization:**
- JWT token caching
- CORS preflight caching
- Efficient routing algorithms
- Minimal latency overhead

**High Availability:**
- Health checks for all services
- Automatic failover
- Graceful degradation
- Monitoring and alerting

Deployment Options
------------------

**Development Environment:**
- Single instance of each service
- Hot reload for code changes
- Detailed logging and debugging
- Easy setup and teardown

**Production Environment:**
- Multiple instances for high availability
- Optimized Docker images
- Production-grade monitoring
- Automated deployment pipelines

**Docker Compose:**
- Easy local development
- Consistent environment
- Service orchestration
- Health checks and dependencies

Monitoring and Observability
----------------------------

**What We Monitor:**
- Service health and availability
- Authentication success/failure rates
- API response times
- Error rates and types
- Resource usage (CPU, memory, disk)

**How We Monitor:**
- Health check endpoints
- Structured logging (JSON format)
- Metrics collection
- Alerting and notifications
- Dashboard visualization

**Key Metrics:**
- Requests per second
- Authentication success rate
- Average response time
- Error rate by endpoint
- Token validation performance

Common Use Cases
----------------

**Use Case 1: Web Application**
1. User logs into web app
2. Web app gets JWT token from Auth Service
3. Web app includes token in API requests
4. Kong validates token and allows access
5. Backend services process requests

**Use Case 2: Mobile Application**
1. User authenticates in mobile app
2. Mobile app stores JWT token securely
3. Mobile app sends token with each API call
4. Kong validates token and routes requests
5. Backend services respond with data

**Use Case 3: Server-to-Server**
1. Service A needs to call Service B
2. Service A gets JWT token from Auth Service
3. Service A includes token in requests to Service B
4. Kong validates token and allows access
5. Service B processes the request

**Use Case 4: Third-Party Integration**
1. Third-party service registers with Auth Service
2. Auth Service creates consumer and JWT token
3. Third-party includes token in API requests
4. Kong validates token and allows access
5. Backend services process third-party requests

Benefits of This Architecture
-----------------------------

**Security Benefits:**
- Centralized authentication
- No sensitive data in tokens
- Automatic token expiration
- Protection against common attacks

**Operational Benefits:**
- Easy to add new services
- Centralized monitoring
- Consistent security policies
- Reduced development complexity

**Scalability Benefits:**
- Horizontal scaling support
- Load balancing capabilities
- Performance optimization
- High availability design

**Developer Benefits:**
- Simple integration
- Clear documentation
- Testing tools included
- Docker-ready deployment

Next Steps
----------

Now that you understand the complete architecture, you can:

1. **Start Building**: Follow the :doc:`../guides/quick-start` guide
2. **Configure Your System**: Learn about :doc:`../guides/configuration`
3. **Test Your Setup**: Use the :doc:`../guides/testing` procedures
4. **Deploy to Production**: Follow the :doc:`../deployment/production` guide
5. **Monitor Your System**: Set up monitoring and alerting

The architecture is designed to be:
- **Easy to understand** - Clear separation of concerns
- **Easy to deploy** - Docker-ready with automation
- **Easy to scale** - Horizontal scaling support
- **Easy to maintain** - Comprehensive monitoring and logging 