JWT Authentication Explained
============================

What is JWT?
------------

JWT stands for **JSON Web Token**. Think of it as a digital passport that proves who you are when you want to access a service. Just like a real passport contains your information and is stamped by authorities, a JWT contains user information and is digitally signed to prove it's authentic.

.. image:: ../_static/images/jwt-structure.png
   :alt: JWT Token Structure
   :align: center

JWT Structure
^^^^^^^^^^^^

A JWT token has three parts, separated by dots (.):

.. code-block:: text

   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9.a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8
   |-- Header --|.|-- Payload --|.|-- Signature --|

1. **Header** (eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9)
   - Contains information about the token type and signing algorithm
   - Always starts with "eyJ" (base64 encoded JSON)

2. **Payload** (eyJpc3MiOiJ0ZXN0IiwiZXhwIjoxNzgyNzkxOTU2LCJpYXQiOjE3NTEyNTU5NTZ9)
   - Contains the actual user data and claims
   - This is where we store information like user ID, expiration time, etc.

3. **Signature** (a8xATaeQhYQL_BYuDFE-0zU8LpRP2AqM6Xw0HTaPEG8)
   - Proves the token hasn't been tampered with
   - Created using a secret key that only the server knows

How JWT Works in Our System
---------------------------

.. image:: ../_static/images/jwt-flow.png
   :alt: JWT Authentication Flow
   :align: center

Step-by-Step Process
^^^^^^^^^^^^^^^^^^^

1. **User Registration/Creation**
   - User provides username (e.g., "john_doe")
   - System creates a "consumer" in Kong (think of it as a user account)
   - System generates a unique secret key for this user

2. **JWT Token Generation**
   - System creates a JWT token with user information
   - Token includes: user ID, expiration time, creation time
   - Token is signed with the user's secret key

3. **Token Usage**
   - User includes the JWT token in their requests
   - Kong Gateway validates the token before allowing access
   - If valid, user gets access; if invalid, access is denied

Detailed Token Generation Process
--------------------------------

Let's break down exactly how we generate a JWT token in our system:

1. **Consumer Creation**
   ```python
   # When a user is created, we:
   consumer_data = {
       "username": "john_doe",
       "custom_id": "optional-custom-id"
   }
   ```

2. **Secret Generation**
   ```python
   # We generate a random secret for this user
   secret = secrets.token_urlsafe(32)  # Creates a 32-byte random string
   secret_base64 = base64.b64encode(secret.encode()).decode()
   ```

3. **JWT Payload Creation**
   ```python
   # We create the token payload with user information
   payload = {
       "iss": "john_doe",           # Issuer (who created the token)
       "exp": 1782791956,           # Expiration time (when token expires)
       "iat": 1751255956            # Issued at (when token was created)
   }
   ```

4. **Token Signing**
   ```python
   # We sign the token with the user's secret
   token = jwt.encode(payload, secret, algorithm="HS256")
   ```

What Each Field Means
^^^^^^^^^^^^^^^^^^^^

* **iss** (Issuer): The username who owns this token
* **exp** (Expiration): When the token becomes invalid (Unix timestamp)
* **iat** (Issued At): When the token was created (Unix timestamp)

Why Base64 Encoding?
^^^^^^^^^^^^^^^^^^^

We encode the secret in base64 because:
- Kong expects secrets in base64 format
- It's a standard way to represent binary data as text
- It ensures compatibility across different systems

Token Validation Process
-----------------------

When a user tries to access a protected endpoint:

1. **Token Extraction**
   - Kong extracts the JWT token from the request header
   - Looks for: `Authorization: Bearer <token>`

2. **Token Decoding**
   - Kong decodes the base64 secret
   - Extracts the payload from the token

3. **Validation Checks**
   - **Signature Verification**: Ensures token wasn't tampered with
   - **Expiration Check**: Ensures token hasn't expired
   - **Issuer Verification**: Ensures token belongs to a valid user

4. **Access Decision**
   - If all checks pass: Allow access
   - If any check fails: Deny access with 401 Unauthorized

Security Features
-----------------

1. **Digital Signatures**
   - Each token is signed with a unique secret
   - Impossible to forge without knowing the secret
   - Any modification invalidates the signature

2. **Expiration Times**
   - Tokens automatically expire after a set time
   - Default: 1 year (31536000 seconds)
   - Prevents long-term token abuse

3. **Unique Secrets**
   - Each user gets their own secret key
   - Compromising one user doesn't affect others
   - Secrets are randomly generated

4. **No Sensitive Data**
   - Tokens don't contain passwords
   - Only contain user identification and timing
   - Safe to transmit over networks

Real-World Analogy
------------------

Think of JWT tokens like **digital concert tickets**:

* **Ticket Creation**: When you buy a ticket, the venue creates a unique ticket with your name, seat number, and show time
* **Ticket Validation**: When you arrive, security checks the ticket's authenticity, your name, and whether the show hasn't started
* **Access Control**: If everything checks out, you get in; if not, you're turned away

In our system:
- **Venue** = Kong Gateway
- **Ticket** = JWT Token
- **Your Name** = Username (iss claim)
- **Show Time** = Expiration time (exp claim)
- **Security Guard** = JWT Plugin in Kong

Common Questions
----------------

**Q: How long do tokens last?**
A: By default, 1 year (31536000 seconds). This can be configured.

**Q: Can tokens be reused?**
A: Yes, until they expire. Each token can be used multiple times.

**Q: What happens if a token is stolen?**
A: The token remains valid until expiration. For high-security applications, implement token revocation.

**Q: Can I see what's in a token?**
A: Yes! The payload is base64 encoded but not encrypted. You can decode it at jwt.io to see the contents.

**Q: Why not just use passwords?**
A: JWT tokens are more secure because they expire, can be revoked, and don't require storing passwords on the server.

Next Steps
----------

Now that you understand JWT authentication, learn about:
- :doc:`../concepts/kong-gateway` - How Kong Gateway works
- :doc:`../concepts/architecture` - Overall system architecture
- :doc:`../guides/quick-start` - How to get started 