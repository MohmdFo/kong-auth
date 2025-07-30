"""
Casdoor Authentication Module
Handles authentication with Casdoor using JWT tokens
"""

import httpx
import jwt
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Casdoor configuration
CASDOOR_ENDPOINT = os.getenv("CASDOOR_ENDPOINT", "https://iam.ai-lab.ir")
CASDOOR_CLIENT_ID = os.getenv("CASDOOR_CLIENT_ID", "f83fb202807419aee818")
CASDOOR_CLIENT_SECRET = os.getenv("CASDOOR_CLIENT_SECRET", "33189aeb03ec21c7fe65ab0d9b00f4ba198bc640")
CASDOOR_ORG_NAME = os.getenv("CASDOOR_ORG_NAME", "built-in")
CASDOOR_APP_NAME = os.getenv("CASDOOR_APP_NAME", "app-built-in")

# Load public key from certificate file
def load_public_key():
    """Load Casdoor public key from certificate file"""
    cert_path = "casdoor_cert.pem"
    try:
        if os.path.exists(cert_path):
            with open(cert_path, 'r') as f:
                return f.read()
        else:
            logger.warning(f"Certificate file {cert_path} not found")
            return ""
    except Exception as e:
        logger.error(f"Error loading certificate: {e}")
        return ""

CASDOOR_PUBLIC_KEY = load_public_key()

# Security scheme
security = HTTPBearer()

class CasdoorUser:
    """Represents an authenticated Casdoor user"""
    def __init__(self, user_data: Dict[str, Any]):
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

class CasdoorAuth:
    """Casdoor authentication handler"""
    
    def __init__(self):
        self.endpoint = CASDOOR_ENDPOINT
        self.client_id = CASDOOR_CLIENT_ID
        self.client_secret = CASDOOR_CLIENT_SECRET
        self.organization = CASDOOR_ORG_NAME
        self.application = CASDOOR_APP_NAME
        self.public_key = CASDOOR_PUBLIC_KEY
        
    async def verify_token(self, token: str) -> CasdoorUser:
        """
        Verify a Casdoor JWT token and return user information
        """
        try:
            # First, try to decode the token to get basic information
            if not self.public_key:
                # If no public key is configured, we'll use introspection endpoint
                return await self._verify_token_introspection(token)
            else:
                # Use public key to verify token
                return await self._verify_token_with_public_key(token)
                
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
    
    async def _verify_token_with_public_key(self, token: str) -> CasdoorUser:
        """Verify token using public key"""
        try:
            # Decode token without verification first to get claims
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            
            # Verify the token signature
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                audience=self.application,
                issuer=self.organization
            )
            
            # Get user information from token or fetch from Casdoor
            user_data = await self._get_user_info(payload.get("sub", ""))
            return CasdoorUser(user_data)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    async def _verify_token_introspection(self, token: str) -> CasdoorUser:
        """Verify token using Casdoor introspection endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                # Use Casdoor's introspection endpoint
                response = await client.post(
                    f"{self.endpoint}/api/get-account",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid token"
                    )
                
                user_data = response.json()
                return CasdoorUser(user_data)
                
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Casdoor: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Authentication service unavailable"
            )
    
    async def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from Casdoor"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.endpoint}/api/get-user?id={user_id}"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    # Return basic user info from token if API call fails
                    return {
                        "owner": self.organization,
                        "name": user_id.split("/")[-1] if "/" in user_id else user_id,
                        "displayName": user_id.split("/")[-1] if "/" in user_id else user_id,
                        "email": "",
                        "phone": "",
                        "avatar": "",
                        "roles": [],
                        "permissions": [],
                        "properties": {}
                    }
                    
        except Exception as e:
            logger.warning(f"Failed to get user info from Casdoor: {str(e)}")
            # Return basic user info
            return {
                "owner": self.organization,
                "name": user_id.split("/")[-1] if "/" in user_id else user_id,
                "displayName": user_id.split("/")[-1] if "/" in user_id else user_id,
                "email": "",
                "phone": "",
                "avatar": "",
                "roles": [],
                "permissions": [],
                "properties": {}
            }

# Global instance
casdoor_auth = CasdoorAuth()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CasdoorUser:
    """
    Dependency to get the current authenticated user
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = credentials.credentials
    return await casdoor_auth.verify_token(token)

async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[CasdoorUser]:
    """
    Dependency to get the current user (optional - doesn't require authentication)
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        return await casdoor_auth.verify_token(token)
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
                detail=f"Access denied. Required roles: {required_roles}"
            )
        
        return user
    
    return role_checker

def require_permissions(required_permissions: list):
    """
    Decorator to require specific permissions for access
    """
    def permission_checker(user: CasdoorUser = Depends(get_current_user)) -> CasdoorUser:
        user_permissions = set(user.permissions)
        required_permissions_set = set(required_permissions)
        
        if not user_permissions.intersection(required_permissions_set):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required permissions: {required_permissions}"
            )
        
        return user
    
    return permission_checker 