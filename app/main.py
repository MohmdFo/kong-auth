from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import jwt
import secrets
import base64
from datetime import datetime, timedelta
import os
from typing import Optional

app = FastAPI(title="Kong Auth Service", description="Service to create Kong consumers and generate JWT tokens")

# Configuration
KONG_ADMIN_URL = os.getenv("KONG_ADMIN_URL", "http://localhost:8006")
JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS", "31536000"))

class ConsumerRequest(BaseModel):
    username: str
    custom_id: Optional[str] = None

class TokenResponse(BaseModel):
    consumer_id: str
    token: str
    expires_at: datetime
    secret: str

@app.get("/")
async def root():
    return {"message": "Kong Auth Service is running"}

@app.post("/create-consumer", response_model=TokenResponse)
async def create_consumer(consumer_data: ConsumerRequest):
    """
    Create a new Kong consumer and generate JWT credentials
    """
    async with httpx.AsyncClient() as client:
        # Create consumer in Kong
        consumer_payload = {
            "username": consumer_data.username
        }
        if consumer_data.custom_id:
            consumer_payload["custom_id"] = consumer_data.custom_id
            
        try:
            consumer_response = await client.post(
                f"{KONG_ADMIN_URL}/consumers/",
                json=consumer_payload
            )
            consumer_response.raise_for_status()
            consumer = consumer_response.json()
            consumer_id = consumer["id"]
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                # Consumer already exists, get the existing consumer
                try:
                    consumer_response = await client.get(
                        f"{KONG_ADMIN_URL}/consumers/{consumer_data.username}"
                    )
                    consumer_response.raise_for_status()
                    consumer = consumer_response.json()
                    consumer_id = consumer["id"]
                except httpx.HTTPStatusError:
                    raise HTTPException(status_code=500, detail="Failed to get existing consumer")
            else:
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
                f"{KONG_ADMIN_URL}/consumers/{consumer_id}/jwt",
                json=jwt_payload
            )
            jwt_response.raise_for_status()
            jwt_credentials = jwt_response.json()
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"Failed to create JWT credentials: {e.response.text}")
        
        # Generate JWT token
        expiration = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION_SECONDS)
        
        payload = {
            "iss": consumer_data.username,  # issuer claim
            "exp": int(expiration.timestamp()),  # expiration time
            "iat": int(datetime.utcnow().timestamp()),  # issued at
        }
        
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        return TokenResponse(
            consumer_id=consumer_id,
            token=token,
            expires_at=expiration,
            secret=secret_base64
        )

@app.get("/consumers")
async def list_consumers():
    """
    List all Kong consumers
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{KONG_ADMIN_URL}/consumers/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"Failed to list consumers: {e.response.text}")

@app.get("/consumers/{consumer_id}")
async def get_consumer(consumer_id: str):
    """
    Get a specific Kong consumer
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{KONG_ADMIN_URL}/consumers/{consumer_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Consumer not found")
            raise HTTPException(status_code=500, detail=f"Failed to get consumer: {e.response.text}")

@app.delete("/consumers/{consumer_id}")
async def delete_consumer(consumer_id: str):
    """
    Delete a Kong consumer
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{KONG_ADMIN_URL}/consumers/{consumer_id}")
            response.raise_for_status()
            return {"message": "Consumer deleted successfully"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Consumer not found")
            raise HTTPException(status_code=500, detail=f"Failed to delete consumer: {e.response.text}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 