"""
Token management views.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from ..casdoor_oidc import CasdoorUser, get_current_user
from ..models import (
    AutoGenerateConsumerResponse,
    DeleteTokenResponse,
    GenerateTokenAutoRequest,
    GenerateTokenResponse,
    MyTokensResponse,
)
from ..services import TokenService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate-token-auto", response_model=GenerateTokenResponse)
async def generate_token_auto(
    request: GenerateTokenAutoRequest = None,
    current_user: CasdoorUser = Depends(get_current_user),
):
    """
    Generate a new JWT token for the current user.
    Optionally provide a custom name for the token.
    Automatically creates the consumer if it doesn't exist.
    """
    username = current_user.name
    token_name = None
    
    if request and request.token_name:
        token_name = request.token_name
    
    logger.info(f"Generating token for user: {username}")
    
    token_service = TokenService()
    
    try:
        result = await token_service.generate_auto_token(username, token_name)
        return GenerateTokenResponse(**result)
    except Exception as e:
        logger.error(f"Failed to generate token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-generate-consumer", response_model=AutoGenerateConsumerResponse)
async def auto_generate_consumer(current_user: CasdoorUser = Depends(get_current_user)):
    """
    Automatically generate a Kong consumer and JWT token based on the current user's Casdoor authentication.
    Creates the consumer if it doesn't exist, then generates a new JWT token.
    All user information is extracted from the Casdoor token automatically.
    """
    username = current_user.name
    logger.info(f"Auto-generating consumer and token for user: {username}")
    
    token_service = TokenService()
    
    try:
        result = await token_service.auto_generate_consumer_and_token(username)
        return AutoGenerateConsumerResponse(**result)
    except Exception as e:
        logger.error(f"Failed to auto-generate consumer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-tokens", response_model=MyTokensResponse)
async def list_my_tokens(current_user: CasdoorUser = Depends(get_current_user)):
    """
    List all JWT credentials for the current user.
    Returns enhanced token information including token names.
    """
    username = current_user.name
    logger.info(f"Listing tokens for user: {username}")
    
    token_service = TokenService()
    
    try:
        result = await token_service.list_user_tokens(username)
        return MyTokensResponse(**result)
    except Exception as e:
        logger.error(f"Failed to list tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/my-tokens/{jwt_id}")
async def delete_my_token(
    jwt_id: str, current_user: CasdoorUser = Depends(get_current_user)
):
    """Delete a JWT credential (token) for the current user."""
    username = current_user.name
    logger.info(f"Deleting token {jwt_id} for user: {username}")
    
    token_service = TokenService()
    
    try:
        success = await token_service.delete_token_by_id(username, jwt_id)
        
        if success:
            return {"message": "Token deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Token not found")
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/my-tokens/by-name/{token_name}", response_model=DeleteTokenResponse)
async def delete_my_token_by_name(
    token_name: str, current_user: CasdoorUser = Depends(get_current_user)
):
    """Delete a JWT credential (token) by its name for the current user."""
    username = current_user.name
    logger.info(f"Deleting token by name '{token_name}' for user: {username}")
    
    token_service = TokenService()
    
    try:
        result = await token_service.delete_token_by_name(username, token_name)
        return DeleteTokenResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete token by name: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
