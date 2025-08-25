"""
Token generation and management service.
"""
import logging
import uuid
from datetime import datetime
from typing import Tuple

from ..metrics.base import (
    ACTIVE_TOKENS_GAUGE,
    JWT_TOKEN_GENERATED_COUNT,
)
from .kong_service import JWTTokenService, KongConsumerService

logger = logging.getLogger(__name__)


class TokenService:
    """High-level service for token management."""
    
    def __init__(self):
        self.kong_service = KongConsumerService()
        self.jwt_service = JWTTokenService()
    
    def get_consumer_uuid(self, username: str) -> str:
        """Generate a deterministic UUID for a consumer."""
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
        return str(uuid.uuid5(namespace, username))
    
    def generate_default_token_name(self, username: str, prefix: str = "token") -> str:
        """Generate a default token name."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{username}_{prefix}_{timestamp}"
    
    async def create_consumer_with_token(self, username: str) -> dict:
        """Create a consumer and generate a JWT token."""
        # Create or get consumer
        consumer, was_created = await self.kong_service.get_or_create_consumer(username)
        
        # Create JWT credentials
        token_name = username  # Use username as token name for backward compatibility
        jwt_credentials, secret, actual_token_name = await self.kong_service.create_jwt_credentials(username, token_name)
        
        # Generate JWT token
        jwt_token, expiration = self.jwt_service.generate_jwt_token(username, actual_token_name, secret)
        
        # Track metrics
        JWT_TOKEN_GENERATED_COUNT.labels(username=username, token_type="consumer").inc()
        ACTIVE_TOKENS_GAUGE.inc()
        
        consumer_uuid = self.get_consumer_uuid(username)
        
        return {
            "username": username,
            "consumer_uuid": consumer_uuid,
            "token": jwt_token,
            "expires_at": expiration,
        }
    
    async def generate_auto_token(self, username: str, token_name: str = None) -> dict:
        """Generate an automatic token for a user."""
        original_token_name = token_name
        if not token_name:
            token_name = self.generate_default_token_name(username)
        
        logger.info(f"Generating auto token for user: {username}, requested_name: {original_token_name}, using_name: {token_name}")
        
        # Ensure consumer exists
        consumer, was_created = await self.kong_service.get_or_create_consumer(username)
        
        # Create JWT credentials
        jwt_credentials, secret, actual_token_name = await self.kong_service.create_jwt_credentials(username, token_name)
        
        if actual_token_name != token_name:
            logger.info(f"Token name changed from '{token_name}' to '{actual_token_name}' due to conflict")
        
        # Generate JWT token
        jwt_token, expiration = self.jwt_service.generate_jwt_token(username, actual_token_name, secret)
        
        # Track metrics
        JWT_TOKEN_GENERATED_COUNT.labels(username=username, token_type="auto").inc()
        ACTIVE_TOKENS_GAUGE.inc()
        
        token_id = jwt_credentials.get("id", actual_token_name)
        
        return {
            "token": jwt_token,
            "expires_at": expiration,
            "token_name": actual_token_name,
            "token_id": token_id,
        }
    
    async def auto_generate_consumer_and_token(self, username: str) -> dict:
        """Auto-generate both consumer and token."""
        token_name = self.generate_default_token_name(username, "auto")
        
        # Create or get consumer
        consumer, consumer_created = await self.kong_service.get_or_create_consumer(username)
        
        # Create JWT credentials
        jwt_credentials, secret, actual_token_name = await self.kong_service.create_jwt_credentials(username, token_name)
        
        # Generate JWT token
        jwt_token, expiration = self.jwt_service.generate_jwt_token(username, actual_token_name, secret)
        
        # Track metrics
        JWT_TOKEN_GENERATED_COUNT.labels(username=username, token_type="auto_generate").inc()
        ACTIVE_TOKENS_GAUGE.inc()
        
        consumer_uuid = self.get_consumer_uuid(username)
        token_id = jwt_credentials.get("id", actual_token_name)
        
        return {
            "username": username,
            "consumer_uuid": consumer_uuid,
            "token": jwt_token,
            "expires_at": expiration,
            "token_name": actual_token_name,
            "token_id": token_id,
            "consumer_created": consumer_created,
        }
    
    async def list_user_tokens(self, username: str) -> dict:
        """List all tokens for a user with enhanced information."""
        tokens = await self.kong_service.list_user_jwt_tokens(username)
        
        enhanced_tokens = []
        for token in tokens:
            if isinstance(token, dict):
                enhanced_token = self.jwt_service.enhance_token_info(token, username)
                enhanced_tokens.append(enhanced_token)
            else:
                logger.warning(f"Unexpected token format: {type(token)} - {token}")
        
        return {
            "username": username,
            "total_tokens": len(enhanced_tokens),
            "tokens": enhanced_tokens,
        }
    
    async def delete_token_by_id(self, username: str, jwt_id: str) -> bool:
        """Delete a token by its ID."""
        return await self.kong_service.delete_jwt_token(username, jwt_id)
    
    async def delete_token_by_name(self, username: str, token_name: str) -> dict:
        """Delete a token by its name."""
        # Find the token
        token = await self.kong_service.find_token_by_name(username, token_name)
        
        if not token:
            raise ValueError(f"Token with name '{token_name}' not found")
        
        # Delete the token
        token_id = token.get("id")
        success = await self.kong_service.delete_jwt_token(username, token_id)
        
        if not success:
            raise ValueError("Failed to delete token")
        
        return {
            "message": "Token deleted successfully",
            "deleted_token_name": token_name,
            "deleted_token_id": token_id,
        }
