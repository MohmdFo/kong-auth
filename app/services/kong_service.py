"""
Kong API service for managing consumers and JWT credentials.
"""
import base64
import logging
import secrets
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import httpx
import jwt

from ..config import KONG_ADMIN_URL, JWT_EXPIRATION_SECONDS
from ..metrics.base import (
    ACTIVE_CONSUMERS_GAUGE,
    ACTIVE_TOKENS_GAUGE,
    CONSUMER_CREATED_COUNT,
    KONG_API_CALLS_COUNT,
    KONG_API_DURATION_SECONDS,
)
from ..middleware.sentry import capture_request_error

logger = logging.getLogger(__name__)


class KongConsumerService:
    """Service for managing Kong consumers and JWT credentials."""
    
    def __init__(self):
        self.kong_admin_url = KONG_ADMIN_URL
        self.jwt_expiration_seconds = JWT_EXPIRATION_SECONDS
    
    async def get_or_create_consumer(self, username: str) -> Tuple[Dict, bool]:
        """
        Get existing consumer or create a new one.
        
        Returns:
            Tuple of (consumer_data, was_created)
        """
        async with httpx.AsyncClient() as client:
            # First, try to get existing consumer
            kong_start_time = time.time()
            response = await client.get(f"{self.kong_admin_url}/consumers/{username}")
            kong_duration = time.time() - kong_start_time
            
            if response.status_code == 200:
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}", method="GET", status="success"
                ).inc()
                KONG_API_DURATION_SECONDS.labels(
                    endpoint=f"/consumers/{username}", method="GET"
                ).observe(kong_duration)
                
                consumer = response.json()
                logger.info(f"Using existing consumer with username: {username}")
                return consumer, False
            
            elif response.status_code == 404:
                # Consumer doesn't exist, create it
                logger.info(f"Consumer {username} not found, creating new consumer")
                return await self._create_consumer(username)
            
            else:
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}", method="GET", status="error"
                ).inc()
                logger.error(f"Failed to check consumer existence: {response.text}")
                raise Exception(f"Failed to check consumer existence: {response.text}")
    
    async def _create_consumer(self, username: str) -> Tuple[Dict, bool]:
        """Create a new consumer in Kong."""
        async with httpx.AsyncClient() as client:
            consumer_payload = {"username": username}
            
            try:
                kong_start_time = time.time()
                response = await client.post(
                    f"{self.kong_admin_url}/consumers/", json=consumer_payload
                )
                kong_duration = time.time() - kong_start_time
                
                response.raise_for_status()
                
                KONG_API_CALLS_COUNT.labels(
                    endpoint="/consumers", method="POST", status="success"
                ).inc()
                KONG_API_DURATION_SECONDS.labels(
                    endpoint="/consumers", method="POST"
                ).observe(kong_duration)
                
                consumer = response.json()
                logger.info(f"Consumer created successfully with username: {username}")
                
                # Track consumer creation
                CONSUMER_CREATED_COUNT.labels(username=username).inc()
                ACTIVE_CONSUMERS_GAUGE.inc()
                
                return consumer, True
                
            except httpx.HTTPStatusError as e:
                KONG_API_CALLS_COUNT.labels(
                    endpoint="/consumers", method="POST", status="error"
                ).inc()
                
                if e.response.status_code == 409:
                    # Consumer already exists, try to get it
                    logger.info(f"Consumer {username} already exists, retrieving...")
                    return await self._get_existing_consumer(username)
                else:
                    logger.error(f"Failed to create consumer: {e.response.text}")
                    capture_request_error(
                        e,
                        request=None,
                        username=username,
                        operation="create_consumer",
                        status_code=e.response.status_code,
                    )
                    raise Exception(f"Failed to create consumer: {e.response.text}")
    
    async def _get_existing_consumer(self, username: str) -> Tuple[Dict, bool]:
        """Get an existing consumer when creation fails due to conflict."""
        async with httpx.AsyncClient() as client:
            try:
                kong_start_time = time.time()
                response = await client.get(f"{self.kong_admin_url}/consumers/{username}")
                kong_duration = time.time() - kong_start_time
                
                response.raise_for_status()
                
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}", method="GET", status="success"
                ).inc()
                KONG_API_DURATION_SECONDS.labels(
                    endpoint=f"/consumers/{username}", method="GET"
                ).observe(kong_duration)
                
                consumer = response.json()
                logger.info(f"Retrieved existing consumer with username: {username}")
                return consumer, False
                
            except httpx.HTTPStatusError as e:
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}", method="GET", status="error"
                ).inc()
                logger.error(f"Failed to get existing consumer: {username}")
                capture_request_error(
                    e,
                    request=None,
                    username=username,
                    operation="get_existing_consumer",
                )
                raise Exception("Failed to get existing consumer")
    
    async def create_jwt_credentials(self, username: str, token_name: str) -> Tuple[Dict, str, str]:
        """
        Create JWT credentials for a consumer.
        
        Returns:
            Tuple of (jwt_credentials, secret, actual_token_name)
        """
        secret = secrets.token_urlsafe(32)
        secret_base64 = base64.b64encode(secret.encode()).decode()
        
        jwt_payload = {
            "key": token_name,
            "secret": secret_base64,
            "algorithm": "HS256",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                kong_start_time = time.time()
                response = await client.post(
                    f"{self.kong_admin_url}/consumers/{username}/jwt", json=jwt_payload
                )
                kong_duration = time.time() - kong_start_time
                
                response.raise_for_status()
                
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}/jwt", method="POST", status="success"
                ).inc()
                KONG_API_DURATION_SECONDS.labels(
                    endpoint=f"/consumers/{username}/jwt", method="POST"
                ).observe(kong_duration)
                
                jwt_credentials = response.json()
                logger.info(f"JWT credentials created for consumer: {username} with token_name: {token_name}")
                
                return jwt_credentials, secret, token_name
                
            except httpx.HTTPStatusError as e:
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}/jwt", method="POST", status="error"
                ).inc()
                
                if e.response.status_code == 409:
                    # Handle duplicate token name
                    logger.warning(f"Token name '{token_name}' already exists for consumer '{username}', handling duplicate...")
                    return await self._handle_duplicate_token_name(username, token_name, secret_base64)
                else:
                    logger.error(f"Failed to create JWT credentials: {e.response.text}")
                    raise Exception(f"Failed to create JWT credentials: {e.response.text}")
    
    async def _handle_duplicate_token_name(
        self, username: str, token_name: str, secret_base64: str
    ) -> Tuple[Dict, str, str]:
        """Handle JWT token name conflicts by generating a unique name."""
        logger.warning(
            f"JWT token name '{token_name}' already exists for consumer '{username}'. "
            "Generating unique name."
        )
        
        # Generate a unique token name
        unique_suffix = str(uuid.uuid4())[:8]
        unique_timestamp = datetime.utcnow().strftime("%H%M%S")
        unique_token_name = f"{token_name}_{unique_timestamp}_{unique_suffix}"
        
        logger.info(f"Retrying with unique token name: {unique_token_name}")
        
        unique_jwt_payload = {
            "key": unique_token_name,
            "secret": secret_base64,
            "algorithm": "HS256",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                retry_start_time = time.time()
                response = await client.post(
                    f"{self.kong_admin_url}/consumers/{username}/jwt",
                    json=unique_jwt_payload,
                )
                retry_duration = time.time() - retry_start_time
                
                response.raise_for_status()
                
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}/jwt", method="POST", status="success"
                ).inc()
                KONG_API_DURATION_SECONDS.labels(
                    endpoint=f"/consumers/{username}/jwt", method="POST"
                ).observe(retry_duration)
                
                jwt_credentials = response.json()
                logger.info(
                    f"JWT credentials created successfully with unique name: {unique_token_name}"
                )
                
                # Decode the secret to return it
                secret = base64.b64decode(secret_base64).decode()
                return jwt_credentials, secret, unique_token_name
                
            except httpx.HTTPStatusError as retry_error:
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}/jwt", method="POST", status="error"
                ).inc()
                logger.error(
                    f"Failed to create JWT credentials even with unique name: {retry_error.response.text}"
                )
                raise Exception(
                    "Unable to create JWT token even with unique name generation"
                )
    
    async def list_consumers(self) -> List[Dict]:
        """List all Kong consumers."""
        async with httpx.AsyncClient() as client:
            try:
                kong_start_time = time.time()
                response = await client.get(f"{self.kong_admin_url}/consumers/")
                kong_duration = time.time() - kong_start_time
                
                response.raise_for_status()
                
                KONG_API_CALLS_COUNT.labels(
                    endpoint="/consumers", method="GET", status="success"
                ).inc()
                KONG_API_DURATION_SECONDS.labels(
                    endpoint="/consumers", method="GET"
                ).observe(kong_duration)
                
                consumers = response.json()
                logger.info(f"Retrieved {len(consumers)} consumers")
                
                # Update the active consumers gauge
                ACTIVE_CONSUMERS_GAUGE.set(len(consumers))
                
                return consumers
                
            except httpx.HTTPStatusError as e:
                KONG_API_CALLS_COUNT.labels(
                    endpoint="/consumers", method="GET", status="error"
                ).inc()
                logger.error(f"Failed to list consumers: {e.response.text}")
                capture_request_error(
                    e,
                    request=None,
                    operation="list_consumers",
                    status_code=e.response.status_code,
                )
                raise Exception(f"Failed to list consumers: {e.response.text}")
    
    async def list_user_jwt_tokens(self, username: str) -> List[Dict]:
        """List all JWT tokens for a user."""
        async with httpx.AsyncClient() as client:
            kong_start_time = time.time()
            response = await client.get(f"{self.kong_admin_url}/consumers/{username}/jwt")
            kong_duration = time.time() - kong_start_time
            
            response.raise_for_status()
            
            KONG_API_CALLS_COUNT.labels(
                endpoint=f"/consumers/{username}/jwt", method="GET", status="success"
            ).inc()
            KONG_API_DURATION_SECONDS.labels(
                endpoint=f"/consumers/{username}/jwt", method="GET"
            ).observe(kong_duration)
            
            response_data = response.json()
            tokens = response_data.get("data", [])
            
            # Update active tokens gauge
            ACTIVE_TOKENS_GAUGE.set(len(tokens))
            
            return tokens
    
    async def delete_jwt_token(self, username: str, jwt_id: str) -> bool:
        """Delete a JWT token by ID."""
        async with httpx.AsyncClient() as client:
            kong_start_time = time.time()
            response = await client.delete(
                f"{self.kong_admin_url}/consumers/{username}/jwt/{jwt_id}"
            )
            kong_duration = time.time() - kong_start_time
            
            if response.status_code == 204:
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}/jwt/{jwt_id}",
                    method="DELETE",
                    status="success",
                ).inc()
                KONG_API_DURATION_SECONDS.labels(
                    endpoint=f"/consumers/{username}/jwt/{jwt_id}", method="DELETE"
                ).observe(kong_duration)
                
                ACTIVE_TOKENS_GAUGE.dec()
                return True
                
            elif response.status_code == 404:
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}/jwt/{jwt_id}",
                    method="DELETE",
                    status="error",
                ).inc()
                return False
            else:
                KONG_API_CALLS_COUNT.labels(
                    endpoint=f"/consumers/{username}/jwt/{jwt_id}",
                    method="DELETE",
                    status="error",
                ).inc()
                capture_request_error(
                    Exception(f"Failed to delete token: {response.text}"),
                    request=None,
                    username=username,
                    jwt_id=jwt_id,
                    status_code=response.status_code,
                )
                raise Exception("Failed to delete token")
    
    async def find_token_by_name(self, username: str, token_name: str) -> Optional[Dict]:
        """Find a JWT token by its name."""
        tokens = await self.list_user_jwt_tokens(username)
        
        for token in tokens:
            if isinstance(token, dict) and token.get("key") == token_name:
                return token
        
        return None


class JWTTokenService:
    """Service for JWT token operations."""
    
    def __init__(self):
        self.jwt_expiration_seconds = JWT_EXPIRATION_SECONDS
    
    def generate_jwt_token(self, username: str, token_name: str, secret: str) -> Tuple[str, datetime]:
        """Generate a JWT token."""
        expiration = datetime.utcnow() + timedelta(seconds=self.jwt_expiration_seconds)
        
        payload = {
            "iss": username,  # Issuer identifies the user
            "kid": token_name,  # Key ID to match Kong credential key
            "exp": int(expiration.timestamp()),  # expiration time
            "iat": int(datetime.utcnow().timestamp()),  # issued at
        }
        
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        logger.info(f"JWT token generated for user: {username}, token_name: {token_name}, expires: {expiration}")
        logger.debug(f"JWT payload: iss={username}, kid={token_name}")
        
        return token, expiration
    
    def enhance_token_info(self, token_data: Dict, username: str) -> Dict:
        """Enhance token data with JWT token and additional info."""
        secret_base64 = token_data.get("secret")
        if not secret_base64:
            logger.warning(f"No secret found for token {token_data.get('key')}")
            return token_data
        
        try:
            secret = base64.b64decode(secret_base64).decode()
        except Exception as e:
            logger.error(f"Failed to decode secret for token {token_data.get('key')}: {e}")
            return token_data
        
        # Generate JWT token
        token_name = token_data.get("key")
        jwt_token, expiration = self.generate_jwt_token(username, token_name, secret)
        
        # Truncate the JWT token for security
        if len(jwt_token) > 20:
            truncated_token = f"{jwt_token[:10]}...{jwt_token[-10:]}"
        else:
            truncated_token = jwt_token
        
        enhanced_token = {
            "id": token_data.get("id"),
            "key": token_data.get("key"),
            "token_name": token_data.get("key"),
            "algorithm": token_data.get("algorithm"),
            "created_at": token_data.get("created_at"),
            "consumer_id": token_data.get("consumer", {}).get("id")
            if token_data.get("consumer")
            else None,
            "rsa_public_key": token_data.get("rsa_public_key"),
            "token": truncated_token,
            "expires_at": expiration,
        }
        
        return enhanced_token
