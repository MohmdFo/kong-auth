from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import httpx
import jwt
import secrets
import base64
from datetime import datetime, timedelta
import os
from typing import Optional
import logging
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import Kong management API
from .kong_api import router as kong_router
# Import Casdoor OIDC authentication
from .casdoor_oidc import get_current_user, get_optional_user, CasdoorUser, require_resource_ownership
# Import token utilities
from .token_utils import extract_username_from_token, get_username_from_request_data

# Setup logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kong Auth Service", 
    description="Service to create Kong consumers, generate JWT tokens, and manage Kong services and routes",
    version="2.0.0"
)

# Include Kong management API
app.include_router(kong_router)

# Configuration
KONG_ADMIN_URL = os.getenv("KONG_ADMIN_URL", "http://localhost:8006")
JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", "31536000"))

NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace

def get_consumer_uuid(username: str) -> str:
    return str(uuid.uuid5(NAMESPACE, username))

class ConsumerRequest(BaseModel):
    username: str

class TokenResponse(BaseModel):
    username: str
    consumer_uuid: str
    token: str
    expires_at: datetime
    secret: str

class GenerateTokenRequest(BaseModel):
    username: str

class GenerateTokenResponse(BaseModel):
    token: str
    expires_at: datetime
    secret: str

class GenerateTokenAutoRequest(BaseModel):
    """
    Request model for generating token with automatic username extraction
    """
    pass

class ListTokensAutoRequest(BaseModel):
    """
    Request model for listing tokens with automatic username extraction
    """
    pass

class DeleteTokenAutoRequest(BaseModel):
    """
    Request model for deleting token with automatic username extraction
    """
    jwt_id: str

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Kong Auth Service is running"}

@app.get("/me")
async def get_current_user_info(current_user: CasdoorUser = Depends(get_current_user)):
    """
    Get information about the currently authenticated user
    """
    logger.info(f"User info requested for: {current_user.name}")
    return {
        "id": current_user.id,
        "name": current_user.name,
        "display_name": current_user.display_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "avatar": current_user.avatar,
        "organization": current_user.organization,
        "roles": current_user.roles,
        "permissions": current_user.permissions
    }

@app.post("/create-consumer", response_model=TokenResponse)
async def create_consumer(
    consumer_data: ConsumerRequest,
    current_user: CasdoorUser = Depends(get_current_user)
):
    """
    Create a new Kong consumer and generate JWT credentials
    Users can only create consumers with their own username
    """
    # Ensure user can only create consumers with their own username
    if consumer_data.username != current_user.name and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=403,
            detail="You can only create consumers with your own username"
        )
    """
    Create a new Kong consumer and generate JWT credentials
    """
    logger.info(f"Creating consumer with username: {consumer_data.username} by user: {current_user.name}")

    async with httpx.AsyncClient() as client:
        # Create consumer in Kong (no custom_id)
        consumer_payload = {
            "username": consumer_data.username
        }
        try:
            consumer_response = await client.post(
                f"{KONG_ADMIN_URL}/consumers/",
                json=consumer_payload
            )
            consumer_response.raise_for_status()
            consumer = consumer_response.json()
            logger.info(f"Consumer created successfully with username: {consumer_data.username}")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                # Consumer already exists, get the existing consumer
                logger.info(f"Consumer {consumer_data.username} already exists, retrieving existing consumer")
                try:
                    consumer_response = await client.get(
                        f"{KONG_ADMIN_URL}/consumers/{consumer_data.username}"
                    )
                    consumer_response.raise_for_status()
                    consumer = consumer_response.json()
                    logger.info(f"Retrieved existing consumer with username: {consumer_data.username}")
                except httpx.HTTPStatusError:
                    logger.error(f"Failed to get existing consumer: {consumer_data.username}")
                    raise HTTPException(status_code=500, detail="Failed to get existing consumer")
            else:
                logger.error(f"Failed to create consumer: {e.response.text}")
                raise HTTPException(status_code=500, detail=f"Failed to create consumer: {e.response.text}")

        # Generate a random secret for JWT
        secret = secrets.token_urlsafe(32)
        secret_base64 = base64.b64encode(secret.encode()).decode()

        # Create JWT credentials for the consumer
        jwt_payload = {
            "key": consumer_data.username,
            "secret": secret_base64,
            "algorithm": "HS256"
        }

        try:
            jwt_response = await client.post(
                f"{KONG_ADMIN_URL}/consumers/{consumer_data.username}/jwt",
                json=jwt_payload
            )
            jwt_response.raise_for_status()
            jwt_credentials = jwt_response.json()
            logger.info(f"JWT credentials created for consumer: {consumer_data.username}")

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to create JWT credentials: {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to create JWT credentials: {e.response.text}")

        # Generate JWT token
        expiration = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION_SECONDS)

        payload = {
            "iss": consumer_data.username,  # issuer claim
            "exp": int(expiration.timestamp()),  # expiration time
            "iat": int(datetime.utcnow().timestamp()),  # issued at
        }

        token = jwt.encode(payload, secret, algorithm="HS256")
        logger.info(f"JWT token generated for consumer: {consumer_data.username}, expires: {expiration}")

        consumer_uuid = get_consumer_uuid(consumer_data.username)

        return TokenResponse(
            username=consumer_data.username,
            consumer_uuid=consumer_uuid,
            token=token,
            expires_at=expiration,
            secret=secret_base64
        )

@app.post("/generate-token", response_model=GenerateTokenResponse)
async def generate_token(
    data: GenerateTokenRequest,
    current_user: CasdoorUser = Depends(get_current_user)
):
    """
    Generate a new JWT token for an existing consumer.
    """
    async with httpx.AsyncClient() as client:
        # Check if consumer exists
        response = await client.get(f"{KONG_ADMIN_URL}/consumers/{data.username}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Consumer not found")

        # Generate a new secret and create JWT credentials in Kong
        secret = secrets.token_urlsafe(32)
        secret_base64 = base64.b64encode(secret.encode()).decode()
        unique_key = str(uuid.uuid4())  # Ensure key is unique
        jwt_payload = {
            "key": unique_key,
            "secret": secret_base64,
            "algorithm": "HS256"
        }
        jwt_response = await client.post(
            f"{KONG_ADMIN_URL}/consumers/{data.username}/jwt",
            json=jwt_payload
        )
        jwt_response.raise_for_status()

        # Generate JWT token
        expiration = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION_SECONDS)
        payload = {
            "iss": data.username,
            "exp": int(expiration.timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return GenerateTokenResponse(
            token=token,
            expires_at=expiration,
            secret=secret_base64
        )

@app.post("/generate-token-auto", response_model=GenerateTokenResponse)
async def generate_token_auto(
    data: GenerateTokenAutoRequest,
    current_user: CasdoorUser = Depends(get_current_user)
):
    """
    Generate a new JWT token for the current user (username extracted from token).
    """
    username = current_user.name
    logger.info(f"Generating token for user: {username}")
    
    async with httpx.AsyncClient() as client:
        # Check if consumer exists
        response = await client.get(f"{KONG_ADMIN_URL}/consumers/{username}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Consumer not found")

        # Generate a new secret and create JWT credentials in Kong
        secret = secrets.token_urlsafe(32)
        secret_base64 = base64.b64encode(secret.encode()).decode()
        unique_key = str(uuid.uuid4())  # Ensure key is unique
        jwt_payload = {
            "key": unique_key,
            "secret": secret_base64,
            "algorithm": "HS256"
        }
        jwt_response = await client.post(
            f"{KONG_ADMIN_URL}/consumers/{username}/jwt",
            json=jwt_payload
        )
        jwt_response.raise_for_status()

        # Generate JWT token
        expiration = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION_SECONDS)
        payload = {
            "iss": username,
            "exp": int(expiration.timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return GenerateTokenResponse(
            token=token,
            expires_at=expiration,
            secret=secret_base64
        )

@app.get("/consumers")
async def list_consumers(
    current_user: CasdoorUser = Depends(get_current_user)
):
    """
    List all Kong consumers
    """
    logger.info(f"Listing all consumers by user: {current_user.name}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{KONG_ADMIN_URL}/consumers/")
            response.raise_for_status()
            consumers = response.json()
            logger.info(f"Retrieved {len(consumers)} consumers")
            return consumers
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to list consumers: {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to list consumers: {e.response.text}")

@app.get("/consumers/{consumer_id}")
async def get_consumer(
    consumer_id: str,
    current_user: CasdoorUser = Depends(require_resource_ownership("consumer_id"))
):
    """
    Get a specific Kong consumer
    """
    logger.info(f"Getting consumer with ID: {consumer_id} by user: {current_user.name}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{KONG_ADMIN_URL}/consumers/{consumer_id}")
            response.raise_for_status()
            consumer = response.json()
            logger.info(f"Retrieved consumer: {consumer.get('username', 'N/A')}")
            return consumer
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Consumer not found: {consumer_id}")
                raise HTTPException(status_code=404, detail="Consumer not found")
            logger.error(f"Failed to get consumer {consumer_id}: {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to get consumer: {e.response.text}")

@app.delete("/consumers/{consumer_id}")
async def delete_consumer(
    consumer_id: str,
    current_user: CasdoorUser = Depends(require_resource_ownership("consumer_id"))
):
    """
    Delete a Kong consumer
    """
    logger.info(f"Deleting consumer with ID: {consumer_id} by user: {current_user.name}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{KONG_ADMIN_URL}/consumers/{consumer_id}")
            response.raise_for_status()
            logger.info(f"Consumer {consumer_id} deleted successfully")
            return {"message": "Consumer deleted successfully"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Consumer not found for deletion: {consumer_id}")
                raise HTTPException(status_code=404, detail="Consumer not found")
            logger.error(f"Failed to delete consumer {consumer_id}: {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to delete consumer: {e.response.text}")

@app.get("/consumers/{username}/tokens")
async def list_tokens(
    username: str,
    current_user: CasdoorUser = Depends(require_resource_ownership("username"))
):
    """
    List all JWT credentials for a consumer.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{KONG_ADMIN_URL}/consumers/{username}/jwt")
        response.raise_for_status()
        return response.json()

@app.get("/my-tokens")
async def list_my_tokens(
    current_user: CasdoorUser = Depends(get_current_user)
):
    """
    List all JWT credentials for the current user (username extracted from token).
    """
    username = current_user.name
    logger.info(f"Listing tokens for user: {username}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{KONG_ADMIN_URL}/consumers/{username}/jwt")
        response.raise_for_status()
        return response.json()

@app.delete("/consumers/{username}/tokens/{jwt_id}")
async def delete_token(
    username: str,
    jwt_id: str,
    current_user: CasdoorUser = Depends(require_resource_ownership("username"))
):
    """
    Delete a JWT credential (token) for a consumer.
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{KONG_ADMIN_URL}/consumers/{username}/jwt/{jwt_id}")
        if response.status_code == 204:
            return {"message": "Token deleted successfully"}
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Token not found")
        else:
            raise HTTPException(status_code=500, detail="Failed to delete token")

@app.delete("/my-tokens/{jwt_id}")
async def delete_my_token(
    jwt_id: str,
    current_user: CasdoorUser = Depends(get_current_user)
):
    """
    Delete a JWT credential (token) for the current user (username extracted from token).
    """
    username = current_user.name
    logger.info(f"Deleting token {jwt_id} for user: {username}")
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{KONG_ADMIN_URL}/consumers/{username}/jwt/{jwt_id}")
        if response.status_code == 204:
            return {"message": "Token deleted successfully"}
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Token not found")
        else:
            raise HTTPException(status_code=500, detail="Failed to delete token")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
