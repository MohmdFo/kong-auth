"""
Consumer management views.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from ..casdoor_oidc import CasdoorUser, get_current_user
from ..models import ConsumerRequest, TokenResponse
from ..services import TokenService, KongConsumerService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create-consumer", response_model=TokenResponse)
async def create_consumer(consumer_data: ConsumerRequest):
    """
    Create a new Kong consumer and generate JWT credentials.
    No authentication required - open endpoint.
    """
    logger.info(f"Creating consumer with username: {consumer_data.username}")
    
    token_service = TokenService()
    
    try:
        result = await token_service.create_consumer_with_token(consumer_data.username)
        return TokenResponse(**result)
    except Exception as e:
        logger.error(f"Failed to create consumer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consumers")
async def list_consumers(current_user: CasdoorUser = Depends(get_current_user)):
    """List all Kong consumers."""
    logger.info(f"Listing all consumers by user: {current_user.name}")
    
    kong_service = KongConsumerService()
    
    try:
        consumers = await kong_service.list_consumers()
        return consumers
    except Exception as e:
        logger.error(f"Failed to list consumers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
