#!/usr/bin/env python3
"""
Simple Token Utility for Casdoor Token Validation
Extracts username and validates tokens from frontend
"""

import json
import base64
from typing import Optional, Dict, Any
from fastapi import HTTPException

def extract_token_from_frontend_data(data: str) -> Optional[str]:
    """
    Extract token from frontend data (JSON string or object)
    """
    try:
        # If it's already a string that looks like a token, return it
        if data.count('.') == 2 and len(data) > 100:
            return data
        
        # Try to parse as JSON
        if isinstance(data, str):
            parsed_data = json.loads(data)
        else:
            parsed_data = data
        
        # Handle different possible structures
        if isinstance(parsed_data, dict):
            # Direct token
            if 'token' in parsed_data:
                return parsed_data['token']
            # State object with token
            elif 'state' in parsed_data and isinstance(parsed_data['state'], dict):
                if 'token' in parsed_data['state']:
                    return parsed_data['state']['token']
        
        return None
    except Exception as e:
        print(f"Error extracting token: {e}")
        return None

def decode_jwt_payload_simple(token: str) -> Optional[Dict[str, Any]]:
    """
    Simple JWT payload decoder without verification
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Decode payload with proper padding
        payload_str = payload_b64 + '=' * (4 - len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_str)
        payload_json = payload_bytes.decode('utf-8')
        
        # Parse JSON
        return json.loads(payload_json)
    except Exception as e:
        print(f"Error decoding JWT payload: {e}")
        return None

def extract_username_from_token(token: str) -> Optional[str]:
    """
    Extract username from Casdoor token
    """
    try:
        payload = decode_jwt_payload_simple(token)
        if not payload:
            return None
        
        # Try different possible username fields
        username = (
            payload.get('preferred_username') or  # OIDC standard
            payload.get('name') or                # Casdoor name field
            payload.get('sub')                    # Subject (user ID)
        )
        
        return username
    except Exception as e:
        print(f"Error extracting username from token: {e}")
        return None

def validate_token_and_get_username(token: str) -> str:
    """
    Validate token and return username
    Raises HTTPException if token is invalid
    """
    username = extract_username_from_token(token)
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: Could not extract username"
        )
    return username

def get_username_from_request_data(request_data: str) -> str:
    """
    Extract username from request data (frontend format)
    """
    token = extract_token_from_frontend_data(request_data)
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: Could not extract token from request data"
        )
    
    return validate_token_and_get_username(token) 