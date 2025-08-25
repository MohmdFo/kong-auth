"""
Casdoor OIDC Authentication Module
Handles OIDC authentication with Casdoor using the official Python SDK
"""

import logging
import os
from typing import Any, Dict, Optional

import jwt
from casdoor import CasdoorSDK
from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from jwt import PyJWKClient
except ImportError:
    # Fallback for older PyJWT versions
    PyJWKClient = None
import json
from datetime import datetime, timedelta

import httpx

logger = logging.getLogger(__name__)

# Casdoor configuration
CASDOOR_ENDPOINT = os.getenv("CASDOOR_ENDPOINT", "https://iam.ai-lab.ir")
CASDOOR_CLIENT_ID = os.getenv("CASDOOR_CLIENT_ID")
CASDOOR_CLIENT_SECRET = os.getenv("CASDOOR_CLIENT_SECRET")
CASDOOR_ORG_NAME = os.getenv("CASDOOR_ORG_NAME")
CASDOOR_APP_NAME = os.getenv("CASDOOR_APP_NAME")
CASDOOR_CERT_PATH = os.getenv("CASDOOR_CERT_PATH")

# Security scheme
security = HTTPBearer()


class CasdoorUser:
    """Represents an authenticated Casdoor user with OIDC claims"""

    def __init__(self, user_data: Dict[str, Any], token_claims: Dict[str, Any]):
        self.id = user_data.get("owner", "") + "/" + user_data.get("name", "")
        self.name = user_data.get("name", "")
        self.display_name = user_data.get("displayName", "")
        self.email = user_data.get("email", "")
        self.phone = user_data.get("phone", "")
        self.avatar = user_data.get("avatar", "")
        self.organization = user_data.get("owner", "")
        self.roles = user_data.get("roles", [])
        self.permissions = user_data.get("permissions", [])
        self.properties = user_data.get("properties", {})

        # OIDC claims from token
        self.sub = token_claims.get("sub", "")
        self.iss = token_claims.get("iss", "")
        self.aud = token_claims.get("aud", "")
        self.exp = token_claims.get("exp", 0)
        self.iat = token_claims.get("iat", 0)

        # Additional OIDC claims
        self.preferred_username = token_claims.get("preferred_username", self.name)
        self.email_verified = token_claims.get("email_verified", False)
        self.family_name = token_claims.get("family_name", "")
        self.given_name = token_claims.get("given_name", "")

    def can_access_resource(self, resource_owner: str) -> bool:
        """Check if user can access a resource based on ownership"""
        # User can access their own resources
        if resource_owner == self.name or resource_owner == self.id:
            return True

        # Admin users can access all resources
        if "admin" in self.roles:
            return True

        # Check specific permissions
        if "manage_all_consumers" in self.permissions:
            return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "email": self.email,
            "phone": self.phone,
            "avatar": self.avatar,
            "organization": self.organization,
            "roles": self.roles,
            "permissions": self.permissions,
            "sub": self.sub,
            "preferred_username": self.preferred_username,
            "email_verified": self.email_verified,
            "family_name": self.family_name,
            "given_name": self.given_name,
        }


class CasdoorOIDC:
    """Casdoor OIDC authentication handler using official SDK"""

    def __init__(self):
        self.endpoint = CASDOOR_ENDPOINT
        self.client_id = CASDOOR_CLIENT_ID
        self.client_secret = CASDOOR_CLIENT_SECRET
        self.organization = CASDOOR_ORG_NAME
        self.application = CASDOOR_APP_NAME

        # Initialize Casdoor SDK
        try:
            self.casdoor = CasdoorSDK(
                self.client_id,
                self.client_secret,
                CASDOOR_CERT_PATH,
                self.organization,
                self.application,
                self.endpoint,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Casdoor SDK: {e}")
            self.casdoor = None

        # Initialize JWKS client for key rotation
        if PyJWKClient:
            self.jwks_client = PyJWKClient(f"{self.endpoint}/.well-known/jwks.json")
        else:
            self.jwks_client = None
            logger.warning(
                "PyJWKClient not available, using certificate-based validation only"
            )

        # Cache for JWKS keys (with expiration)
        self._jwks_cache = {}
        self._jwks_cache_expiry = None

    async def verify_token(self, token: str) -> CasdoorUser:
        """
        Verify a Casdoor JWT token using OIDC standards
        """
        try:
            if self.jwks_client:
                # Use JWKS for key rotation
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                key = signing_key.key
            else:
                # Fallback to certificate-based validation
                key = self._load_certificate_key()

            # Decode and verify the token
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.endpoint,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )

            # Extract user information from token or fetch from Casdoor
            user_data = await self._get_user_info(payload.get("sub", ""))

            return CasdoorUser(user_data, payload)

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Token verification failed")

    def _load_certificate_key(self):
        """Load certificate key for JWT validation"""
        try:
            if os.path.exists(CASDOOR_CERT_PATH):
                with open(CASDOOR_CERT_PATH, "r") as f:
                    return f.read()
            else:
                logger.error(f"Certificate file {CASDOOR_CERT_PATH} not found")
                raise HTTPException(status_code=500, detail="Certificate not available")
        except Exception as e:
            logger.error(f"Error loading certificate: {e}")
            raise HTTPException(status_code=500, detail="Certificate loading failed")

    async def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from Casdoor"""
        if self.casdoor:
            try:
                # Try to get user info using Casdoor SDK
                # The SDK might not have a direct get_user method, so we'll use the API
                user = self.casdoor.get_user(user_id)
                if user:
                    return user
            except Exception as e:
                logger.warning(f"Failed to get user info via SDK: {str(e)}")

        try:
            # Fallback: try direct API call
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.endpoint}/api/get-user?id={user_id}", timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.warning(f"Failed to get user info via API: {str(e)}")

        # Return basic user info if all else fails
        return {
            "owner": self.organization,
            "name": user_id.split("/")[-1] if "/" in user_id else user_id,
            "displayName": user_id.split("/")[-1] if "/" in user_id else user_id,
            "email": "",
            "phone": "",
            "avatar": "",
            "roles": [],
            "permissions": [],
            "properties": {},
        }

    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get the authorization URL for OIDC login"""
        if not self.casdoor:
            raise HTTPException(status_code=500, detail="Casdoor SDK not available")

        return self.casdoor.get_auth_link(
            redirect_uri=redirect_uri,
            response_type="code",
            scope="openid profile email",
            state=state,
        )

    async def exchange_code_for_token(
        self, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        if not self.casdoor:
            raise HTTPException(status_code=500, detail="Casdoor SDK not available")

        try:
            token_response = self.casdoor.get_oauth_token(
                code=code, redirect_uri=redirect_uri
            )
            return token_response
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Failed to exchange authorization code"
            )


# Global instance
casdoor_oidc = CasdoorOIDC()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CasdoorUser:
    """
    Get the current authenticated user from the JWT token
    Falls back to simple token extraction if OIDC verification fails
    """
    token = credentials.credentials

    try:
        # Try full OIDC verification first
        casdoor_oidc = CasdoorOIDC()
        return await casdoor_oidc.verify_token(token)
    except Exception as e:
        logger.warning(
            f"OIDC verification failed, falling back to simple extraction: {e}"
        )

        # Fallback: Use simple token extraction
        try:
            from .token_utils import extract_username_from_token

            username = extract_username_from_token(token)
            if not username:
                raise HTTPException(
                    status_code=401, detail="Invalid token: Could not extract username"
                )

            # Create a basic CasdoorUser with minimal data
            user_data = {
                "owner": "built-in",
                "name": username,
                "displayName": username,
                "email": "",
                "phone": "",
                "avatar": "",
                "roles": [],
                "permissions": [],
                "properties": {},
            }

            # Create token claims from simple extraction
            import jwt

            token_claims = jwt.decode(token, options={"verify_signature": False})

            return CasdoorUser(user_data, token_claims)

        except Exception as fallback_error:
            logger.error(f"Fallback authentication also failed: {fallback_error}")
            raise HTTPException(status_code=401, detail="Invalid token")


async def get_optional_user(
    authorization: Optional[str] = Header(None),
) -> Optional[CasdoorUser]:
    """
    Dependency to get the current user (optional - doesn't require authentication)
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.replace("Bearer ", "")
        return await casdoor_oidc.verify_token(token)
    except HTTPException:
        return None


def require_roles(required_roles: list):
    """
    Decorator to require specific roles for access
    """

    def role_checker(user: CasdoorUser = Depends(get_current_user)) -> CasdoorUser:
        user_roles = set(user.roles)
        required_roles_set = set(required_roles)

        if not user_roles.intersection(required_roles_set):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {required_roles}",
            )

        return user

    return role_checker


def require_permissions(required_permissions: list):
    """
    Decorator to require specific permissions for access
    """

    def permission_checker(
        user: CasdoorUser = Depends(get_current_user),
    ) -> CasdoorUser:
        user_permissions = set(user.permissions)
        required_permissions_set = set(required_permissions)

        if not user_permissions.intersection(required_permissions_set):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required permissions: {required_permissions}",
            )

        return user

    return permission_checker


def require_resource_ownership(resource_owner_field: str = "username"):
    """
    Decorator to ensure users can only access their own resources
    """

    def ownership_checker(
        request: Request, user: CasdoorUser = Depends(get_current_user)
    ) -> CasdoorUser:
        # Get the resource owner from request parameters or body
        resource_owner = None

        # Check path parameters
        if resource_owner_field in request.path_params:
            resource_owner = request.path_params[resource_owner_field]

        # Check query parameters
        if not resource_owner and resource_owner_field in request.query_params:
            resource_owner = request.query_params[resource_owner_field]

        # If we found a resource owner, check access
        if resource_owner and not user.can_access_resource(resource_owner):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. You can only access your own resources.",
            )

        return user

    return ownership_checker


# Middleware for logging authenticated requests
async def log_authenticated_request(request: Request, call_next):
    """Middleware to log authenticated requests"""
    response = await call_next(request)

    # Log authenticated requests
    if "user" in request.state:
        user = request.state.user
        logger.info(
            f"Authenticated request: {request.method} {request.url.path} "
            f"by user: {user.name} (roles: {user.roles})"
        )

    return response
