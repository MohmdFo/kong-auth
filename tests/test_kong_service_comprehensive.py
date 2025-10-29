"""
Comprehensive tests for KongConsumerService and JWTTokenService
Tests all logic flows, edge cases, error handling, and business logic
"""
import base64
import secrets
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

import httpx
import jwt
import pytest

from app.services.kong_service import KongConsumerService, JWTTokenService


class MockHTTPResponse:
    """Mock HTTP response for testing"""
    
    def __init__(self, status_code: int, json_data: Dict[str, Any] = None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
    
    def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            error = httpx.HTTPStatusError(
                message=f"HTTP {self.status_code}",
                request=Mock(),
                response=self
            )
            raise error


@pytest.fixture
def kong_service():
    """Fixture for KongConsumerService"""
    return KongConsumerService()


@pytest.fixture
def jwt_service():
    """Fixture for JWTTokenService"""
    return JWTTokenService()


class TestKongConsumerService:
    """Comprehensive tests for KongConsumerService"""
    
    @pytest.mark.asyncio
    async def test_get_or_create_consumer_existing(self, kong_service):
        """Test getting an existing consumer"""
        username = "test_user"
        expected_consumer = {"id": "123", "username": username}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.return_value = MockHTTPResponse(200, expected_consumer)
            
            consumer, was_created = await kong_service.get_or_create_consumer(username)
            
            assert consumer == expected_consumer
            assert was_created is False
            mock_client.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_or_create_consumer_not_found_creates_new(self, kong_service):
        """Test creating a new consumer when it doesn't exist"""
        username = "new_user"
        expected_consumer = {"id": "456", "username": username}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # First call returns 404 (not found)
            mock_client.get.return_value = MockHTTPResponse(404)
            # Second call creates the consumer
            mock_client.post.return_value = MockHTTPResponse(201, expected_consumer)
            
            consumer, was_created = await kong_service.get_or_create_consumer(username)
            
            assert consumer == expected_consumer
            assert was_created is True
    
    @pytest.mark.asyncio
    async def test_get_or_create_consumer_get_error(self, kong_service):
        """Test error handling when getting consumer fails"""
        username = "error_user"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.return_value = MockHTTPResponse(500, text="Internal Server Error")
            
            with pytest.raises(Exception, match="Failed to check consumer existence"):
                await kong_service.get_or_create_consumer(username)
    
    @pytest.mark.asyncio
    async def test_create_consumer_success(self, kong_service):
        """Test successful consumer creation"""
        username = "new_consumer"
        expected_consumer = {"id": "789", "username": username}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.post.return_value = MockHTTPResponse(201, expected_consumer)
            
            consumer, was_created = await kong_service._create_consumer(username)
            
            assert consumer == expected_consumer
            assert was_created is True
    
    @pytest.mark.asyncio
    async def test_create_consumer_conflict_409(self, kong_service):
        """Test handling 409 conflict when creating consumer"""
        username = "existing_user"
        existing_consumer = {"id": "999", "username": username}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # POST returns 409 conflict
            post_response = MockHTTPResponse(409, text="Consumer already exists")
            mock_client.post.return_value = post_response
            
            # GET returns the existing consumer
            mock_client.get.return_value = MockHTTPResponse(200, existing_consumer)
            
            consumer, was_created = await kong_service._create_consumer(username)
            
            assert consumer == existing_consumer
            assert was_created is False
    
    @pytest.mark.asyncio
    async def test_create_consumer_error(self, kong_service):
        """Test error handling when creating consumer fails"""
        username = "error_user"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.post.return_value = MockHTTPResponse(500, text="Database error")
            
            with pytest.raises(Exception, match="Failed to create consumer"):
                await kong_service._create_consumer(username)
    
    @pytest.mark.asyncio
    async def test_create_jwt_credentials_success(self, kong_service):
        """Test successful JWT credential creation"""
        username = "test_user"
        token_name = "my_token"
        expected_credentials = {
            "id": "cred_123",
            "key": token_name,
            "algorithm": "HS256"
        }
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.post.return_value = MockHTTPResponse(201, expected_credentials)
            
            credentials, secret, actual_name = await kong_service.create_jwt_credentials(
                username, token_name
            )
            
            assert credentials == expected_credentials
            assert isinstance(secret, str)
            assert actual_name == token_name
    
    @pytest.mark.asyncio
    async def test_create_jwt_credentials_duplicate_token_name(self, kong_service):
        """Test handling duplicate token name (409 conflict)"""
        username = "test_user"
        token_name = "duplicate_token"
        unique_credentials = {
            "id": "cred_456",
            "key": "duplicate_token_123456_abcd1234",
            "algorithm": "HS256"
        }
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # First POST returns 409 conflict
            post_response_1 = MockHTTPResponse(409, text="Duplicate key")
            # Second POST with unique name succeeds
            post_response_2 = MockHTTPResponse(201, unique_credentials)
            
            mock_client.post.side_effect = [post_response_1, post_response_2]
            
            credentials, secret, actual_name = await kong_service.create_jwt_credentials(
                username, token_name
            )
            
            assert credentials == unique_credentials
            assert actual_name != token_name  # Name should be modified
            assert token_name in actual_name  # Should contain original name
    
    @pytest.mark.asyncio
    async def test_create_jwt_credentials_persistent_error(self, kong_service):
        """Test error when credential creation fails even with unique name"""
        username = "test_user"
        token_name = "error_token"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Both attempts fail
            mock_client.post.return_value = MockHTTPResponse(500, text="Server error")
            
            with pytest.raises(Exception):
                await kong_service.create_jwt_credentials(username, token_name)
    
    @pytest.mark.asyncio
    async def test_list_consumers_success(self, kong_service):
        """Test listing all consumers"""
        expected_consumers = [
            {"id": "1", "username": "user1"},
            {"id": "2", "username": "user2"},
            {"id": "3", "username": "user3"}
        ]
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.return_value = MockHTTPResponse(200, expected_consumers)
            
            consumers = await kong_service.list_consumers()
            
            assert consumers == expected_consumers
            assert len(consumers) == 3
    
    @pytest.mark.asyncio
    async def test_list_consumers_error(self, kong_service):
        """Test error handling when listing consumers fails"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.return_value = MockHTTPResponse(500, text="Server error")
            
            with pytest.raises(Exception, match="Failed to list consumers"):
                await kong_service.list_consumers()
    
    @pytest.mark.asyncio
    async def test_list_user_jwt_tokens_success(self, kong_service):
        """Test listing user's JWT tokens"""
        username = "test_user"
        expected_tokens = {
            "data": [
                {"id": "token1", "key": "token_name_1"},
                {"id": "token2", "key": "token_name_2"}
            ]
        }
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.return_value = MockHTTPResponse(200, expected_tokens)
            
            tokens = await kong_service.list_user_jwt_tokens(username)
            
            assert tokens == expected_tokens["data"]
            assert len(tokens) == 2
    
    @pytest.mark.asyncio
    async def test_list_user_jwt_tokens_empty(self, kong_service):
        """Test listing tokens when user has none"""
        username = "no_tokens_user"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.return_value = MockHTTPResponse(200, {"data": []})
            
            tokens = await kong_service.list_user_jwt_tokens(username)
            
            assert tokens == []
    
    @pytest.mark.asyncio
    async def test_delete_jwt_token_success(self, kong_service):
        """Test successful token deletion"""
        username = "test_user"
        jwt_id = "token_123"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.delete.return_value = MockHTTPResponse(204)
            
            result = await kong_service.delete_jwt_token(username, jwt_id)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_jwt_token_not_found(self, kong_service):
        """Test deleting non-existent token"""
        username = "test_user"
        jwt_id = "nonexistent_token"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.delete.return_value = MockHTTPResponse(404)
            
            result = await kong_service.delete_jwt_token(username, jwt_id)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_jwt_token_error(self, kong_service):
        """Test error handling when deleting token"""
        username = "test_user"
        jwt_id = "token_123"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.delete.return_value = MockHTTPResponse(500, text="Server error")
            
            with pytest.raises(Exception, match="Failed to delete token"):
                await kong_service.delete_jwt_token(username, jwt_id)
    
    @pytest.mark.asyncio
    async def test_find_token_by_name_found(self, kong_service):
        """Test finding token by name when it exists"""
        username = "test_user"
        token_name = "my_token"
        expected_token = {"id": "token_123", "key": token_name}
        
        with patch.object(
            kong_service, "list_user_jwt_tokens", return_value=[
                {"id": "token_1", "key": "other_token"},
                expected_token,
                {"id": "token_3", "key": "another_token"}
            ]
        ):
            token = await kong_service.find_token_by_name(username, token_name)
            
            assert token == expected_token
    
    @pytest.mark.asyncio
    async def test_find_token_by_name_not_found(self, kong_service):
        """Test finding token by name when it doesn't exist"""
        username = "test_user"
        token_name = "nonexistent_token"
        
        with patch.object(
            kong_service, "list_user_jwt_tokens", return_value=[
                {"id": "token_1", "key": "other_token"},
                {"id": "token_2", "key": "another_token"}
            ]
        ):
            token = await kong_service.find_token_by_name(username, token_name)
            
            assert token is None


class TestJWTTokenService:
    """Comprehensive tests for JWTTokenService"""
    
    def test_generate_jwt_token_success(self, jwt_service):
        """Test successful JWT token generation"""
        username = "test_user"
        token_name = "test_token"
        secret = "test_secret_key"
        
        token, expiration = jwt_service.generate_jwt_token(username, token_name, secret)
        
        # Decode and verify token
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        
        assert decoded["iss"] == username
        assert decoded["kid"] == token_name
        assert "exp" in decoded
        assert "iat" in decoded
        assert isinstance(expiration, datetime)
    
    def test_generate_jwt_token_expiration_time(self, jwt_service):
        """Test that token expiration is set correctly"""
        username = "test_user"
        token_name = "test_token"
        secret = "test_secret_key"
        
        before_time = datetime.utcnow()
        token, expiration = jwt_service.generate_jwt_token(username, token_name, secret)
        after_time = datetime.utcnow()
        
        # Expiration should be approximately jwt_expiration_seconds from now
        expected_min = before_time + timedelta(seconds=jwt_service.jwt_expiration_seconds)
        expected_max = after_time + timedelta(seconds=jwt_service.jwt_expiration_seconds)
        
        assert expected_min <= expiration <= expected_max
    
    def test_generate_jwt_token_unique_tokens(self, jwt_service):
        """Test that different tokens are generated for different users"""
        secret = "shared_secret"
        
        token1, _ = jwt_service.generate_jwt_token("user1", "token1", secret)
        token2, _ = jwt_service.generate_jwt_token("user2", "token2", secret)
        
        assert token1 != token2
    
    def test_enhance_token_info_success(self, jwt_service):
        """Test enhancing token info with JWT generation"""
        username = "test_user"
        secret = "test_secret"
        secret_base64 = base64.b64encode(secret.encode()).decode()
        
        token_data = {
            "id": "token_123",
            "key": "my_token",
            "secret": secret_base64,
            "algorithm": "HS256",
            "created_at": 1234567890,
            "consumer": {"id": "consumer_123"}
        }
        
        enhanced = jwt_service.enhance_token_info(token_data, username)
        
        assert enhanced["id"] == "token_123"
        assert enhanced["key"] == "my_token"
        assert enhanced["token_name"] == "my_token"
        assert enhanced["algorithm"] == "HS256"
        assert enhanced["created_at"] == 1234567890
        assert enhanced["consumer_id"] == "consumer_123"
        assert "token" in enhanced
        assert "expires_at" in enhanced
    
    def test_enhance_token_info_no_secret(self, jwt_service):
        """Test enhancing token info when secret is missing"""
        username = "test_user"
        token_data = {
            "id": "token_123",
            "key": "my_token",
            "algorithm": "HS256"
        }
        
        enhanced = jwt_service.enhance_token_info(token_data, username)
        
        # Should return original data when secret is missing
        assert enhanced == token_data
    
    def test_enhance_token_info_invalid_secret(self, jwt_service):
        """Test enhancing token info with invalid base64 secret"""
        username = "test_user"
        token_data = {
            "id": "token_123",
            "key": "my_token",
            "secret": "invalid_base64!!!",
            "algorithm": "HS256"
        }
        
        enhanced = jwt_service.enhance_token_info(token_data, username)
        
        # Should return original data when secret decoding fails
        assert enhanced == token_data
    
    def test_enhance_token_info_token_truncation(self, jwt_service):
        """Test that generated JWT token is truncated for security"""
        username = "test_user"
        secret = "long_secret_key_for_testing"
        secret_base64 = base64.b64encode(secret.encode()).decode()
        
        token_data = {
            "id": "token_123",
            "key": "my_token",
            "secret": secret_base64,
            "algorithm": "HS256"
        }
        
        enhanced = jwt_service.enhance_token_info(token_data, username)
        
        # Token should be truncated
        assert "..." in enhanced["token"]
        assert len(enhanced["token"]) < 50  # Truncated version should be short


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.mark.asyncio
    async def test_consumer_with_special_characters(self, kong_service):
        """Test handling usernames with special characters"""
        username = "user@example.com"
        expected_consumer = {"id": "123", "username": username}
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_client.get.return_value = MockHTTPResponse(200, expected_consumer)
            
            consumer, _ = await kong_service.get_or_create_consumer(username)
            
            assert consumer["username"] == username
    
    @pytest.mark.asyncio
    async def test_empty_token_list(self, kong_service):
        """Test handling empty token list response"""
        username = "test_user"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Response with no 'data' key
            mock_client.get.return_value = MockHTTPResponse(200, {})
            
            tokens = await kong_service.list_user_jwt_tokens(username)
            
            assert tokens == []
    
    @pytest.mark.asyncio
    async def test_malformed_token_response(self, kong_service):
        """Test handling malformed token in list"""
        username = "test_user"
        token_name = "my_token"
        
        with patch.object(
            kong_service, "list_user_jwt_tokens", return_value=[
                "invalid_string_token",  # Not a dict
                {"id": "token_2", "key": "other_token"},
                None,  # None value
                {"id": "token_4"}  # Missing 'key'
            ]
        ):
            token = await kong_service.find_token_by_name(username, token_name)
            
            assert token is None  # Should handle malformed data gracefully
    
    def test_jwt_token_with_minimal_expiration(self, jwt_service):
        """Test JWT generation with very short expiration"""
        # Temporarily set short expiration
        original_expiration = jwt_service.jwt_expiration_seconds
        jwt_service.jwt_expiration_seconds = 1  # 1 second
        
        try:
            username = "test_user"
            token_name = "short_lived_token"
            secret = "test_secret"
            
            token, expiration = jwt_service.generate_jwt_token(username, token_name, secret)
            
            # Decode without verification to avoid expiration error during test
            decoded = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_exp": False})
            assert decoded["exp"] - decoded["iat"] <= 2  # Should be ~1 second
        finally:
            jwt_service.jwt_expiration_seconds = original_expiration
    
    @pytest.mark.asyncio
    async def test_concurrent_token_creation(self, kong_service):
        """Test handling concurrent token creation attempts"""
        username = "test_user"
        token_name = "concurrent_token"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Track what name is sent in the second request
            actual_generated_name = None
            
            def post_side_effect(*args, **kwargs):
                nonlocal actual_generated_name
                if "json" in kwargs and "key" in kwargs["json"]:
                    key = kwargs["json"]["key"]
                    if key != token_name:  # This is the retry with unique name
                        actual_generated_name = key
                        return MockHTTPResponse(201, {
                            "id": "token_unique",
                            "key": key,  # Return the generated name
                            "algorithm": "HS256"
                        })
                # First request with original name
                return MockHTTPResponse(409, text="Already exists")
            
            mock_client.post.side_effect = post_side_effect
            
            credentials, secret, actual_name = await kong_service.create_jwt_credentials(
                username, token_name
            )
            
            # Should get unique name on retry (with timestamp and random suffix)
            assert actual_name != token_name
            assert actual_name.startswith(f"{token_name}_")  # Check it has the prefix
            assert credentials["key"] == actual_name
            assert actual_generated_name == actual_name  # Verify the name matches what was generated


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
