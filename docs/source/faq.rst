Frequently Asked Questions (FAQ)
===============================

Common questions and answers about Kong Auth Service.

General Questions
-----------------

**Q: What is Kong Auth Service?**
A: Kong Auth Service is a complete authentication solution that combines Kong Gateway with JWT token authentication. It provides secure API access with easy user management and token generation.

**Q: Who should use Kong Auth Service?**
A: Anyone who needs to secure APIs or applications with JWT authentication. This includes developers, DevOps engineers, system administrators, and businesses that need secure API access.

**Q: Is Kong Auth Service free to use?**
A: Yes, Kong Auth Service is open source and free to use. Kong Gateway itself is also open source, though Kong offers enterprise features for additional cost.

**Q: What programming languages are supported?**
A: Kong Auth Service works with any programming language that can make HTTP requests. The JWT tokens are standard and can be used with any client library.

**Q: Can I use this in production?**
A: Yes, Kong Auth Service is designed for production use. It includes Docker containers, health checks, monitoring, and security best practices.

JWT Token Questions
-------------------

**Q: What is a JWT token?**
A: JWT stands for JSON Web Token. It's a secure way to transmit information between parties as a JSON object. Think of it as a digital passport that proves your identity.

**Q: How long do JWT tokens last?**
A: By default, JWT tokens last for 1 year (31,536,000 seconds). This can be configured in the Auth Service settings.

**Q: Can JWT tokens be reused?**
A: Yes, JWT tokens can be used multiple times until they expire. Each token is valid for all requests until the expiration time.

**Q: What happens if a JWT token is stolen?**
A: The token remains valid until expiration. For high-security applications, you should implement token revocation or use shorter expiration times.

**Q: Can I see what's inside a JWT token?**
A: Yes! JWT tokens are base64 encoded but not encrypted. You can decode them at jwt.io to see the contents (payload).

**Q: Why not just use passwords instead of JWT tokens?**
A: JWT tokens are more secure because they expire automatically, can be revoked, and don't require storing passwords on the server.

Kong Gateway Questions
----------------------

**Q: What is Kong Gateway?**
A: Kong Gateway is an API gateway that sits in front of your services and handles authentication, routing, and security. Think of it as a security guard for your APIs.

**Q: Why do we use Kong Gateway?**
A: Kong Gateway provides centralized security, reduces complexity, improves performance, and makes it easy to add new security rules.

**Q: What are Kong plugins?**
A: Kong plugins are modules that add functionality to Kong Gateway. We use the JWT plugin for authentication and the CORS plugin for web application support.

**Q: Can I use Kong Auth Service without Kong Gateway?**
A: No, Kong Gateway is a core component of the system. It handles the JWT token validation and routing to backend services.

**Q: How does Kong Gateway validate JWT tokens?**
A: Kong Gateway uses the JWT plugin to extract tokens from requests, verify their digital signatures, check expiration times, and validate the issuer.

Installation and Setup
---------------------

**Q: What do I need to install Kong Auth Service?**
A: You need Docker and Docker Compose. The system runs entirely in containers, so no other software installation is required.

**Q: How long does it take to set up Kong Auth Service?**
A: The initial setup takes about 5-10 minutes. Most of this time is downloading Docker images. Once downloaded, subsequent starts take less than 1 minute.

**Q: Can I run Kong Auth Service on Windows?**
A: Yes, Kong Auth Service runs on Windows using Docker Desktop. Make sure you have Docker Desktop installed and WSL2 enabled.

**Q: What ports does Kong Auth Service use?**
A: The default ports are:
- 8000: Auth Service
- 8001: Sample Service (direct access)
- 8005: Kong Gateway (protected endpoints)
- 8006: Kong Admin API

**Q: Can I change the default ports?**
A: Yes, you can change the ports by modifying the docker-compose.yml file or using environment variables.

**Q: Do I need to install Kong separately?**
A: No, Kong Gateway is included in the Docker Compose setup and will be automatically downloaded and configured.

Configuration Questions
-----------------------

**Q: How do I configure JWT token expiration?**
A: You can configure token expiration by modifying the JWT_EXPIRATION_SECONDS environment variable in the Auth Service.

**Q: Can I restrict CORS to specific domains?**
A: Yes, you can modify the CORS plugin configuration in Kong to only allow specific origins instead of all origins (*).

**Q: How do I add more backend services?**
A: You can add new services by creating new service definitions in Kong and adding them to the Docker Compose configuration.

**Q: Can I use a different database for Kong?**
A: Yes, Kong supports PostgreSQL and Cassandra. You can configure a custom database by modifying the Kong configuration.

**Q: How do I enable HTTPS/SSL?**
A: You can enable HTTPS by adding SSL certificates to Kong Gateway and configuring the appropriate routes.

Security Questions
------------------

**Q: Is Kong Auth Service secure?**
A: Yes, Kong Auth Service implements security best practices including JWT token validation, digital signatures, automatic expiration, and secure secret management.

**Q: How are secrets stored?**
A: Secrets are stored in Kong's database and are base64 encoded. Each user gets a unique secret that's used to sign their JWT tokens.

**Q: Can someone forge a JWT token?**
A: No, JWT tokens are digitally signed with a secret key. Without knowing the secret, it's computationally impossible to create a valid token.

**Q: What happens if Kong Gateway is compromised?**
A: If Kong Gateway is compromised, an attacker could potentially access protected services. However, the JWT tokens themselves remain secure due to their digital signatures.

**Q: Should I use Kong Auth Service for financial applications?**
A: Kong Auth Service provides strong security, but for financial applications, you should also implement additional security measures like rate limiting, audit logging, and compliance features.

Performance Questions
---------------------

**Q: How many requests can Kong Auth Service handle?**
A: Kong Gateway can handle thousands of requests per second. The actual performance depends on your hardware and configuration.

**Q: Does JWT validation slow down requests?**
A: JWT validation adds minimal overhead (typically less than 10ms per request). The performance impact is negligible for most applications.

**Q: Can I scale Kong Auth Service horizontally?**
A: Yes, you can run multiple instances of Kong Gateway behind a load balancer for horizontal scaling.

**Q: How much memory does Kong Auth Service use?**
A: The total memory usage is typically 500MB-1GB depending on the number of services and plugins configured.

**Q: Can I monitor Kong Auth Service performance?**
A: Yes, Kong provides metrics and logging that you can use for monitoring. You can also integrate with monitoring tools like Prometheus and Grafana.

Troubleshooting Questions
-------------------------

**Q: Why am I getting "401 Unauthorized" errors?**
A: This usually means your JWT token is invalid, expired, or missing. Check that you're including the token in the Authorization header.

**Q: Why am I getting CORS errors in my browser?**
A: CORS errors occur when making cross-origin requests. This is normal for direct API calls. Use a tool like curl or Postman for testing.

**Q: Why won't the services start?**
A: Check that Docker is running, ports are available, and you have sufficient disk space. Check the Docker logs for specific error messages.

**Q: How do I check if Kong Gateway is working?**
A: You can check Kong Gateway health by calling the Kong Admin API: `curl http://localhost:8006/status`

**Q: Why is my JWT token not working?**
A: Common issues include:
- Token has expired
- Token format is incorrect
- Secret key is wrong
- Token is not in the Authorization header

**Q: How do I reset everything and start fresh?**
A: You can reset everything by running:
```bash
docker-compose down -v
docker-compose up -d
```

Integration Questions
--------------------

**Q: How do I integrate Kong Auth Service with my existing application?**
A: You can integrate by:
1. Creating users through the Auth Service API
2. Getting JWT tokens for authentication
3. Including tokens in your API requests
4. Configuring your services behind Kong Gateway

**Q: Can I use Kong Auth Service with mobile apps?**
A: Yes, mobile apps can use JWT tokens just like web applications. Store the token securely in the mobile app and include it in API requests.

**Q: How do I integrate with a web application?**
A: Web applications can:
1. Call the Auth Service to create users and get tokens
2. Store tokens securely (e.g., in HTTP-only cookies)
3. Include tokens in API requests to Kong Gateway

**Q: Can I use Kong Auth Service with microservices?**
A: Yes, Kong Auth Service is designed for microservices architectures. Each service can be protected by Kong Gateway with consistent authentication.

**Q: How do I handle user registration and login?**
A: You can build a registration/login system that:
1. Creates users through the Auth Service API
2. Manages user sessions with JWT tokens
3. Handles token refresh and expiration

Production Questions
--------------------

**Q: How do I deploy Kong Auth Service to production?**
A: Follow the production deployment guide which covers Docker deployment, environment configuration, monitoring, and security hardening.

**Q: What monitoring should I set up?**
A: Set up monitoring for:
- Service health and availability
- Authentication success/failure rates
- API response times
- Error rates and types
- Resource usage

**Q: How do I backup Kong Auth Service data?**
A: Backup the Kong database and any custom configurations. The Auth Service itself is stateless and doesn't require backup.

**Q: Can I use Kong Auth Service in a cloud environment?**
A: Yes, Kong Auth Service works in any cloud environment that supports Docker. It's compatible with AWS, Azure, Google Cloud, and others.

**Q: How do I handle high availability?**
A: For high availability, run multiple instances of Kong Gateway behind a load balancer and use a shared database for Kong.

**Q: What's the difference between development and production?**
A: Production environments should include:
- HTTPS/SSL encryption
- Proper monitoring and logging
- Security hardening
- Performance optimization
- Backup and recovery procedures

Still Have Questions?
---------------------

If you couldn't find the answer to your question:

1. **Check the Documentation**: Review the other sections of this documentation
2. **Search the Issues**: Look for similar questions in the GitHub issues
3. **Ask the Community**: Join our community discussions
4. **Report a Bug**: If you found a bug, report it with detailed information

Remember: There are no stupid questions! We're here to help you succeed with Kong Auth Service. 