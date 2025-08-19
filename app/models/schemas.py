"""
Pydantic models for request/response schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ConsumerRequest(BaseModel):
    """Request model for creating a consumer."""
    username: str


class TokenResponse(BaseModel):
    """Response model for token generation."""
    username: str
    consumer_uuid: str
    token: str
    expires_at: datetime


class GenerateTokenAutoRequest(BaseModel):
    """Request model for automatic token generation."""
    token_name: Optional[str] = None
    description: Optional[str] = None


class GenerateTokenResponse(BaseModel):
    """Response model for automatic token generation."""
    token: str
    expires_at: datetime
    token_name: str
    token_id: str


class TokenInfo(BaseModel):
    """Model for token information."""
    id: str
    key: str
    token_name: str
    algorithm: str
    created_at: Optional[int] = None
    consumer_id: Optional[str] = None
    rsa_public_key: Optional[str] = None
    token: Optional[str] = None
    expires_at: Optional[datetime] = None


class MyTokensResponse(BaseModel):
    """Response model for user's tokens."""
    username: str
    total_tokens: int
    tokens: list[TokenInfo]


class DeleteTokenResponse(BaseModel):
    """Response model for token deletion."""
    message: str
    deleted_token_name: Optional[str] = None
    deleted_token_id: Optional[str] = None


class AutoGenerateConsumerResponse(BaseModel):
    """Response model for auto-generated consumer and token."""
    username: str
    consumer_uuid: str
    token: str
    expires_at: datetime
    token_name: str
    token_id: str
    consumer_created: bool  # True if consumer was created, False if it already existed
