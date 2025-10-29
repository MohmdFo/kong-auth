"""
Comprehensive tests for API views/endpoints
Tests all routes, authentication, authorization, and error handling
"""
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
import pytest
import jwt as pyjwt
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.casdoor_oidc import CasdoorUser
from app.models.schemas import (
    ConsumerRequest,
    GenerateTokenAutoRequest,
)


@pytest.fixture
def valid_jwt_token():
    """Fixture for creating a valid JWT token"""
    secret = "test_secret"
    claims = {
        "sub": "organization_sharif/test_user",
        "iss": "https://iam.ai-lab.ir",
        "aud": "test_client",
        "exp": 9999999999,
        "iat": 1234567890,
        "preferred_username": "test_user"
    }
    return pyjwt.encode(claims, secret, algorithm="HS256")


@pytest.fixture
def mock_casdoor_user():
    """Fixture for mock authenticated user"""
    user_data = {
        "owner": "organization_sharif",
        "name": "test_user",
        "displayName": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "avatar": "https://example.com/avatar.jpg",
        "roles": ["user"],
        "permissions": ["read:tokens"],
        "properties": {}
    }
    token_claims = {
        "sub": "organization_sharif/test_user",
        "iss": "https://iam.ai-lab.ir",
        "aud": "test_client",
        "exp": 9999999999,
        "iat": 1234567890,
        "preferred_username": "test_user",
        "email_verified": True,
        "family_name": "User",
        "given_name": "Test"
    }
    return CasdoorUser(user_data, token_claims)


@pytest.fixture
def mock_admin_user():
    """Fixture for mock admin user"""
    user_data = {
        "owner": "organization_sharif",
        "name": "admin_user",
        "displayName": "Admin User",
        "email": "admin@example.com",
        "phone": "+1234567890",
        "avatar": "https://example.com/avatar.jpg",
        "roles": ["admin", "user"],
        "permissions": ["read:tokens", "write:tokens", "manage_all_consumers"],
        "properties": {}
    }
    token_claims = {
        "sub": "organization_sharif/admin_user",
        "iss": "https://iam.ai-lab.ir",
        "aud": "test_client",
        "exp": 9999999999,
        "iat": 1234567890
    }
    return CasdoorUser(user_data, token_claims)


class TestAuthViews:
    """Tests for authentication-related views"""
    
    def test_root_endpoint(self):
        """Test root endpoint is accessible"""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Kong Auth Service" in response.json()["message"]
    
    def test_me_endpoint_authenticated(self, mock_casdoor_user, valid_jwt_token):
        """Test /me endpoint with authenticated user"""
        from app.views.auth_views import get_current_user
        
        app.dependency_overrides[get_current_user] = lambda: mock_casdoor_user
        client = TestClient(app)
        
        try:
            response = client.get(
                "/me",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "test_user"
            assert data["email"] == "test@example.com"
            assert "roles" in data
            assert "permissions" in data
        finally:
            app.dependency_overrides.clear()
    
    def test_me_endpoint_unauthenticated(self):
        """Test /me endpoint without authentication"""
        client = TestClient(app)
        
        response = client.get("/me")
        
        assert response.status_code == 403  # No auth header


class TestConsumerViews:
    """Tests for consumer management views"""
    
    def test_create_consumer_success(self):
        """Test successful consumer creation"""
        client = TestClient(app)
        
        mock_result = {
            "username": "new_user",
            "consumer_uuid": "uuid-123",
            "token": "jwt.token.here",
            "expires_at": datetime.utcnow()
        }
        
        with patch("app.services.token_service.TokenService.create_consumer_with_token",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.post(
                "/create-consumer",
                json={"username": "new_user"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "new_user"
            assert "token" in data
    
    def test_create_consumer_invalid_input(self):
        """Test consumer creation with invalid input"""
        client = TestClient(app)
        
        # Missing username
        response = client.post("/create-consumer", json={})
        assert response.status_code == 422  # Validation error
    
    def test_create_consumer_service_error(self):
        """Test consumer creation when service fails"""
        client = TestClient(app)
        
        with patch("app.services.token_service.TokenService.create_consumer_with_token",
                   new_callable=AsyncMock, side_effect=Exception("Kong unavailable")):
            response = client.post(
                "/create-consumer",
                json={"username": "error_user"}
            )
            
            assert response.status_code == 500
            assert "Failed to create consumer" in response.json()["detail"]
    
    def test_list_consumers_authenticated(self, mock_admin_user, valid_jwt_token):
        """Test listing consumers with authentication"""
        client = TestClient(app)
        
        mock_consumers = [
            {"id": "1", "username": "user1"},
            {"id": "2", "username": "user2"}
        ]
        
        with patch("app.views.consumer_views.get_current_user", return_value=mock_admin_user), \
             patch("app.services.kong_service.KongConsumerService.list_consumers",
                   new_callable=AsyncMock, return_value=mock_consumers):
            response = client.get(
                "/consumers",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    def test_list_consumers_unauthenticated(self):
        """Test listing consumers without authentication"""
        client = TestClient(app)
        
        response = client.get("/consumers")
        assert response.status_code == 403


class TestTokenViews:
    """Tests for token management views"""
    
    def test_generate_token_auto_with_name(self, mock_casdoor_user, valid_jwt_token):
        """Test generating token with custom name"""
        client = TestClient(app)
        
        mock_result = {
            "token": "jwt.token.here",
            "expires_at": datetime.utcnow(),
            "token_name": "my_custom_token",
            "token_id": "token_123"
        }
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.generate_auto_token",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.post(
                "/generate-token-auto",
                json={"token_name": "my_custom_token"},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["token_name"] == "my_custom_token"
            assert "token" in data
    
    def test_generate_token_auto_without_name(self, mock_casdoor_user, valid_jwt_token):
        """Test generating token without custom name (uses default)"""
        client = TestClient(app)
        
        mock_result = {
            "token": "jwt.token.here",
            "expires_at": datetime.utcnow(),
            "token_name": "test_user_token_20250101_120000",
            "token_id": "token_456"
        }
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.generate_auto_token",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.post(
                "/generate-token-auto",
                json={},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "test_user" in data["token_name"]
    
    def test_generate_token_auto_unauthenticated(self):
        """Test generating token without authentication"""
        client = TestClient(app)
        
        response = client.post(
            "/generate-token-auto",
            json={"token_name": "test"}
        )
        
        assert response.status_code == 403
    
    def test_generate_token_auto_service_error(self, mock_casdoor_user, valid_jwt_token):
        """Test token generation when service fails"""
        client = TestClient(app)
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.generate_auto_token",
                   new_callable=AsyncMock, side_effect=Exception("Token generation failed")):
            response = client.post(
                "/generate-token-auto",
                json={},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 500
    
    def test_auto_generate_consumer_success(self, mock_casdoor_user, valid_jwt_token):
        """Test auto-generating consumer and token"""
        client = TestClient(app)
        
        mock_result = {
            "username": "test_user",
            "consumer_uuid": "uuid-789",
            "token": "jwt.token.here",
            "expires_at": datetime.utcnow(),
            "token_name": "auto_token",
            "token_id": "token_789",
            "consumer_created": True
        }
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.auto_generate_consumer_and_token",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.post(
                "/auto-generate-consumer",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "test_user"
            assert data["consumer_created"] is True
    
    def test_list_my_tokens_success(self, mock_casdoor_user, valid_jwt_token):
        """Test listing user's tokens"""
        client = TestClient(app)
        
        mock_result = {
            "username": "test_user",
            "total_tokens": 2,
            "tokens": [
                {
                    "id": "token1",
                    "key": "name1",
                    "token_name": "name1",
                    "algorithm": "HS256",
                    "created_at": 1234567890,
                    "consumer_id": "consumer_123",
                    "rsa_public_key": None,
                    "token": "jwt...token",
                    "expires_at": None
                },
                {
                    "id": "token2",
                    "key": "name2",
                    "token_name": "name2",
                    "algorithm": "HS256",
                    "created_at": 1234567891,
                    "consumer_id": "consumer_123",
                    "rsa_public_key": None,
                    "token": "jwt...token2",
                    "expires_at": None
                }
            ]
        }
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.list_user_tokens",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.get(
                "/my-tokens",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_tokens"] == 2
            assert len(data["tokens"]) == 2
    
    def test_list_my_tokens_empty(self, mock_casdoor_user, valid_jwt_token):
        """Test listing tokens when user has none"""
        client = TestClient(app)
        
        mock_result = {
            "username": "test_user",
            "total_tokens": 0,
            "tokens": []
        }
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.list_user_tokens",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.get(
                "/my-tokens",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_tokens"] == 0
    
    def test_delete_my_token_by_id_success(self, mock_casdoor_user, valid_jwt_token):
        """Test successful token deletion by ID"""
        client = TestClient(app)
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.delete_token_by_id",
                   new_callable=AsyncMock, return_value=True):
            response = client.delete(
                "/my-tokens/token_123",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            assert "deleted successfully" in response.json()["message"]
    
    def test_delete_my_token_by_id_value_error(self, mock_casdoor_user, valid_jwt_token):
        """Test handling ValueError when deleting token"""
        client = TestClient(app)
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.delete_token_by_id",
                   new_callable=AsyncMock, side_effect=ValueError("Invalid token ID")):
            response = client.delete(
                "/my-tokens/invalid_id",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 404
    
    def test_delete_my_token_by_name_success(self, mock_casdoor_user, valid_jwt_token):
        """Test successful token deletion by name"""
        client = TestClient(app)
        
        mock_result = {
            "message": "Token deleted successfully",
            "deleted_token_name": "my_token",
            "deleted_token_id": "token_123"
        }
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.delete_token_by_name",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.delete(
                "/my-tokens/by-name/my_token",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["deleted_token_name"] == "my_token"
    
    def test_delete_my_token_by_name_not_found(self, mock_casdoor_user, valid_jwt_token):
        """Test deleting non-existent token by name"""
        client = TestClient(app)
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.delete_token_by_name",
                   new_callable=AsyncMock, side_effect=ValueError("Token not found")):
            response = client.delete(
                "/my-tokens/by-name/nonexistent",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 404


class TestViewsEdgeCases:
    """Edge cases and error scenarios for views"""
    
    def test_create_consumer_empty_username(self):
        """Test creating consumer with empty username"""
        client = TestClient(app)
        
        response = client.post(
            "/create-consumer",
            json={"username": ""}
        )
        
        # Should fail validation or service logic
        assert response.status_code in [400, 422, 500]
    
    def test_create_consumer_very_long_username(self):
        """Test creating consumer with very long username"""
        client = TestClient(app)
        
        long_username = "a" * 1000
        mock_result = {
            "username": long_username,
            "consumer_uuid": "uuid",
            "token": "token",
            "expires_at": datetime.utcnow()
        }
        
        with patch("app.services.token_service.TokenService.create_consumer_with_token",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.post(
                "/create-consumer",
                json={"username": long_username}
            )
            
            # Should handle long usernames
            assert response.status_code in [200, 400, 422]
    
    def test_generate_token_with_special_characters_in_name(self, mock_casdoor_user, valid_jwt_token):
        """Test generating token with special characters in name"""
        client = TestClient(app)
        
        special_name = "token-name_with.special@chars!"
        mock_result = {
            "token": "jwt.token",
            "expires_at": datetime.utcnow(),
            "token_name": special_name,
            "token_id": "token_special"
        }
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.generate_auto_token",
                   new_callable=AsyncMock, return_value=mock_result):
            response = client.post(
                "/generate-token-auto",
                json={"token_name": special_name},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            # Should handle special characters
            assert response.status_code in [200, 400, 422]
    
    def test_delete_token_with_malformed_id(self, mock_casdoor_user, valid_jwt_token):
        """Test deleting token with malformed ID"""
        client = TestClient(app)
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.delete_token_by_id",
                   new_callable=AsyncMock, side_effect=ValueError("Malformed ID")):
            response = client.delete(
                "/my-tokens/malformed@id#123",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response.status_code == 404
    
    def test_concurrent_requests_same_user(self, mock_casdoor_user, valid_jwt_token):
        """Test handling concurrent requests from same user"""
        client = TestClient(app)
        
        mock_result = {
            "token": "jwt.token",
            "expires_at": datetime.utcnow(),
            "token_name": "concurrent_token",
            "token_id": "token_concurrent"
        }
        
        with patch("app.views.token_views.get_current_user", return_value=mock_casdoor_user), \
             patch("app.services.token_service.TokenService.generate_auto_token",
                   new_callable=AsyncMock, return_value=mock_result):
            # Simulate concurrent requests
            response1 = client.post(
                "/generate-token-auto",
                json={"token_name": "token1"},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            response2 = client.post(
                "/generate-token-auto",
                json={"token_name": "token2"},
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )
            
            assert response1.status_code == 200
            assert response2.status_code == 200


class TestAuthorizationLogic:
    """Tests for authorization and access control"""
    
    def test_casdoor_user_can_access_own_resource(self):
        """Test that user can access their own resources"""
        user_data = {
            "owner": "org",
            "name": "test_user",
            "displayName": "Test",
            "email": "test@example.com",
            "phone": "",
            "avatar": "",
            "roles": ["user"],
            "permissions": [],
            "properties": {}
        }
        token_claims = {"sub": "org/test_user", "iss": "issuer", "aud": "aud", "exp": 9999999999, "iat": 1234567890}
        user = CasdoorUser(user_data, token_claims)
        
        assert user.can_access_resource("test_user") is True
        assert user.can_access_resource("org/test_user") is True
    
    def test_casdoor_user_cannot_access_others_resource(self):
        """Test that user cannot access other users' resources"""
        user_data = {
            "owner": "org",
            "name": "test_user",
            "displayName": "Test",
            "email": "test@example.com",
            "phone": "",
            "avatar": "",
            "roles": ["user"],
            "permissions": [],
            "properties": {}
        }
        token_claims = {"sub": "org/test_user", "iss": "issuer", "aud": "aud", "exp": 9999999999, "iat": 1234567890}
        user = CasdoorUser(user_data, token_claims)
        
        assert user.can_access_resource("other_user") is False
    
    def test_admin_can_access_all_resources(self):
        """Test that admin can access all resources"""
        user_data = {
            "owner": "org",
            "name": "admin_user",
            "displayName": "Admin",
            "email": "admin@example.com",
            "phone": "",
            "avatar": "",
            "roles": ["admin"],
            "permissions": [],
            "properties": {}
        }
        token_claims = {"sub": "org/admin_user", "iss": "issuer", "aud": "aud", "exp": 9999999999, "iat": 1234567890}
        user = CasdoorUser(user_data, token_claims)
        
        assert user.can_access_resource("any_user") is True
        assert user.can_access_resource("other_user") is True
    
    def test_user_with_manage_all_permission_can_access_all(self):
        """Test that user with manage_all_consumers permission can access all resources"""
        user_data = {
            "owner": "org",
            "name": "manager_user",
            "displayName": "Manager",
            "email": "manager@example.com",
            "phone": "",
            "avatar": "",
            "roles": ["user"],
            "permissions": ["manage_all_consumers"],
            "properties": {}
        }
        token_claims = {"sub": "org/manager_user", "iss": "issuer", "aud": "aud", "exp": 9999999999, "iat": 1234567890}
        user = CasdoorUser(user_data, token_claims)
        
        assert user.can_access_resource("any_user") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
