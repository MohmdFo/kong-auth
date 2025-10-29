"""
Comprehensive tests for TokenService
Tests all business logic, edge cases, and integration flows
"""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
import pytest

from app.services.token_service import TokenService


@pytest.fixture
def token_service():
    """Fixture for TokenService"""
    return TokenService()


class TestTokenService:
    """Comprehensive tests for TokenService"""
    
    def test_get_consumer_uuid_deterministic(self, token_service):
        """Test that UUID generation is deterministic"""
        username = "test_user"
        
        uuid1 = token_service.get_consumer_uuid(username)
        uuid2 = token_service.get_consumer_uuid(username)
        
        assert uuid1 == uuid2
        assert isinstance(uuid.UUID(uuid1), uuid.UUID)
    
    def test_get_consumer_uuid_unique_per_user(self, token_service):
        """Test that different users get different UUIDs"""
        uuid1 = token_service.get_consumer_uuid("user1")
        uuid2 = token_service.get_consumer_uuid("user2")
        
        assert uuid1 != uuid2
    
    def test_generate_default_token_name(self, token_service):
        """Test default token name generation"""
        username = "test_user"
        prefix = "token"
        
        token_name = token_service.generate_default_token_name(username, prefix)
        
        assert username in token_name
        assert prefix in token_name
        assert "_" in token_name
    
    def test_generate_default_token_name_custom_prefix(self, token_service):
        """Test token name generation with custom prefix"""
        username = "test_user"
        prefix = "custom"
        
        token_name = token_service.generate_default_token_name(username, prefix)
        
        assert username in token_name
        assert prefix in token_name
    
    def test_generate_default_token_name_unique(self, token_service):
        """Test that token names are unique (time-based)"""
        import time
        username = "test_user"
        
        name1 = token_service.generate_default_token_name(username)
        time.sleep(1.1)  # Wait just over 1 second to ensure timestamp changes
        name2 = token_service.generate_default_token_name(username)
        
        # Names should be different due to timestamp
        assert name1 != name2
    
    @pytest.mark.asyncio
    async def test_create_consumer_with_token_new_consumer(self, token_service):
        """Test creating consumer with token when consumer doesn't exist"""
        username = "new_user"
        consumer_data = {"id": "consumer_123", "username": username}
        jwt_credentials = {"id": "jwt_123", "key": username}
        secret = "test_secret"
        token = "mock.jwt.token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, True)
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, username)
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.create_consumer_with_token(username)
            
            assert result["username"] == username
            assert result["token"] == token
            assert result["expires_at"] == expiration
            assert "consumer_uuid" in result
    
    @pytest.mark.asyncio
    async def test_create_consumer_with_token_existing_consumer(self, token_service):
        """Test creating token for existing consumer"""
        username = "existing_user"
        consumer_data = {"id": "consumer_456", "username": username}
        jwt_credentials = {"id": "jwt_456", "key": username}
        secret = "test_secret"
        token = "mock.jwt.token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, False)  # Already exists
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, username)
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.create_consumer_with_token(username)
            
            assert result["username"] == username
            assert result["token"] == token
    
    @pytest.mark.asyncio
    async def test_generate_auto_token_with_custom_name(self, token_service):
        """Test generating auto token with custom name"""
        username = "test_user"
        token_name = "my_custom_token"
        consumer_data = {"id": "consumer_789", "username": username}
        jwt_credentials = {"id": "jwt_789", "key": token_name}
        secret = "test_secret"
        token = "mock.jwt.token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, False)
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, token_name)
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.generate_auto_token(username, token_name)
            
            assert result["token"] == token
            assert result["token_name"] == token_name
            assert result["token_id"] == "jwt_789"
            assert result["expires_at"] == expiration
    
    @pytest.mark.asyncio
    async def test_generate_auto_token_without_name(self, token_service):
        """Test generating auto token without custom name (uses default)"""
        username = "test_user"
        consumer_data = {"id": "consumer_001", "username": username}
        jwt_credentials = {"id": "jwt_001", "key": "auto_generated_name"}
        secret = "test_secret"
        token = "mock.jwt.token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, False)
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, "auto_generated_name")
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.generate_auto_token(username, None)
            
            assert result["token"] == token
            assert "token_name" in result
    
    @pytest.mark.asyncio
    async def test_generate_auto_token_name_conflict_resolution(self, token_service):
        """Test handling token name conflicts with automatic resolution"""
        username = "test_user"
        original_name = "my_token"
        resolved_name = "my_token_123456_abc"
        consumer_data = {"id": "consumer_002", "username": username}
        jwt_credentials = {"id": "jwt_002", "key": resolved_name}
        secret = "test_secret"
        token = "mock.jwt.token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, False)
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, resolved_name)  # Name changed
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.generate_auto_token(username, original_name)
            
            assert result["token_name"] == resolved_name
            assert result["token_name"] != original_name
    
    @pytest.mark.asyncio
    async def test_auto_generate_consumer_and_token_new_consumer(self, token_service):
        """Test auto-generating both consumer and token (new consumer)"""
        username = "brand_new_user"
        consumer_data = {"id": "consumer_new", "username": username}
        jwt_credentials = {"id": "jwt_new", "key": "auto_token_new"}
        secret = "test_secret"
        token = "mock.jwt.token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, True)  # Consumer created
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, "auto_token_new")
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.auto_generate_consumer_and_token(username)
            
            assert result["username"] == username
            assert result["token"] == token
            assert result["consumer_created"] is True
            assert "consumer_uuid" in result
            assert "token_name" in result
            assert "token_id" in result
    
    @pytest.mark.asyncio
    async def test_auto_generate_consumer_and_token_existing_consumer(self, token_service):
        """Test auto-generating token for existing consumer"""
        username = "existing_user"
        consumer_data = {"id": "consumer_exist", "username": username}
        jwt_credentials = {"id": "jwt_exist", "key": "auto_token_exist"}
        secret = "test_secret"
        token = "mock.jwt.token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, False)  # Consumer already exists
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, "auto_token_exist")
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.auto_generate_consumer_and_token(username)
            
            assert result["consumer_created"] is False
    
    @pytest.mark.asyncio
    async def test_list_user_tokens_success(self, token_service):
        """Test listing user tokens with enhancement"""
        username = "test_user"
        raw_tokens = [
            {"id": "token1", "key": "name1", "secret": "c2VjcmV0MQ=="},
            {"id": "token2", "key": "name2", "secret": "c2VjcmV0Mg=="}
        ]
        enhanced_token = {"id": "token1", "key": "name1", "token": "enhanced"}
        
        with patch.object(
            token_service.kong_service, "list_user_jwt_tokens",
            return_value=raw_tokens
        ), patch.object(
            token_service.jwt_service, "enhance_token_info",
            return_value=enhanced_token
        ):
            result = await token_service.list_user_tokens(username)
            
            assert result["username"] == username
            assert result["total_tokens"] == 2
            assert len(result["tokens"]) == 2
    
    @pytest.mark.asyncio
    async def test_list_user_tokens_empty(self, token_service):
        """Test listing tokens when user has none"""
        username = "no_tokens_user"
        
        with patch.object(
            token_service.kong_service, "list_user_jwt_tokens",
            return_value=[]
        ):
            result = await token_service.list_user_tokens(username)
            
            assert result["username"] == username
            assert result["total_tokens"] == 0
            assert result["tokens"] == []
    
    @pytest.mark.asyncio
    async def test_list_user_tokens_with_invalid_tokens(self, token_service):
        """Test handling invalid token formats in list"""
        username = "test_user"
        raw_tokens = [
            {"id": "token1", "key": "name1"},  # Valid dict
            "invalid_string",  # Invalid: not a dict
            None,  # Invalid: None
            {"id": "token2", "key": "name2"}  # Valid dict
        ]
        enhanced_token = {"id": "token", "key": "name"}
        
        with patch.object(
            token_service.kong_service, "list_user_jwt_tokens",
            return_value=raw_tokens
        ), patch.object(
            token_service.jwt_service, "enhance_token_info",
            return_value=enhanced_token
        ):
            result = await token_service.list_user_tokens(username)
            
            # Should only process valid dict tokens
            assert result["total_tokens"] == 2  # Only 2 valid dicts
    
    @pytest.mark.asyncio
    async def test_delete_token_by_id_success(self, token_service):
        """Test successful token deletion by ID"""
        username = "test_user"
        jwt_id = "token_to_delete"
        
        with patch.object(
            token_service.kong_service, "delete_jwt_token",
            return_value=True
        ):
            result = await token_service.delete_token_by_id(username, jwt_id)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_token_by_id_not_found(self, token_service):
        """Test deleting non-existent token by ID"""
        username = "test_user"
        jwt_id = "nonexistent_token"
        
        with patch.object(
            token_service.kong_service, "delete_jwt_token",
            return_value=False
        ):
            result = await token_service.delete_token_by_id(username, jwt_id)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_token_by_name_found(self, token_service):
        """Test deleting token by name when it exists"""
        username = "test_user"
        token_name = "my_token"
        found_token = {"id": "token_123", "key": token_name}
        
        with patch.object(
            token_service.kong_service, "find_token_by_name",
            return_value=found_token
        ), patch.object(
            token_service.kong_service, "delete_jwt_token",
            return_value=True
        ):
            result = await token_service.delete_token_by_name(username, token_name)
            
            assert "message" in result
            assert result["deleted_token_name"] == token_name
            assert result["deleted_token_id"] == "token_123"
    
    @pytest.mark.asyncio
    async def test_delete_token_by_name_not_found(self, token_service):
        """Test deleting token by name when it doesn't exist"""
        username = "test_user"
        token_name = "nonexistent_token"
        
        with patch.object(
            token_service.kong_service, "find_token_by_name",
            return_value=None
        ):
            with pytest.raises(ValueError, match="Token.*not found"):
                await token_service.delete_token_by_name(username, token_name)
    
    @pytest.mark.asyncio
    async def test_delete_token_by_name_deletion_fails(self, token_service):
        """Test handling deletion failure after finding token"""
        username = "test_user"
        token_name = "my_token"
        found_token = {"id": "token_456", "key": token_name}
        
        with patch.object(
            token_service.kong_service, "find_token_by_name",
            return_value=found_token
        ), patch.object(
            token_service.kong_service, "delete_jwt_token",
            return_value=False
        ):
            with pytest.raises(Exception):
                await token_service.delete_token_by_name(username, token_name)


class TestTokenServiceEdgeCases:
    """Edge cases and boundary conditions for TokenService"""
    
    @pytest.mark.asyncio
    async def test_consumer_creation_with_special_characters(self, token_service):
        """Test handling usernames with special characters"""
        username = "user+test@example.com"
        consumer_data = {"id": "consumer_special", "username": username}
        jwt_credentials = {"id": "jwt_special", "key": "token_special"}
        secret = "secret"
        token = "token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, True)
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, "token_special")
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.create_consumer_with_token(username)
            
            assert result["username"] == username
    
    @pytest.mark.asyncio
    async def test_very_long_token_name(self, token_service):
        """Test handling very long token names"""
        username = "test_user"
        long_token_name = "a" * 500  # Very long name
        consumer_data = {"id": "consumer_long", "username": username}
        jwt_credentials = {"id": "jwt_long", "key": long_token_name}
        secret = "secret"
        token = "token"
        expiration = datetime.utcnow()
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, False)
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, long_token_name)
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            return_value=(token, expiration)
        ):
            result = await token_service.generate_auto_token(username, long_token_name)
            
            assert result["token_name"] == long_token_name
    
    @pytest.mark.asyncio
    async def test_concurrent_token_generation(self, token_service):
        """Test multiple tokens generated for same user"""
        username = "concurrent_user"
        consumer_data = {"id": "consumer_concurrent", "username": username}
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, False)
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            side_effect=[
                ({"id": "jwt1", "key": "token1"}, "secret1", "token1"),
                ({"id": "jwt2", "key": "token2"}, "secret2", "token2"),
                ({"id": "jwt3", "key": "token3"}, "secret3", "token3"),
            ]
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            side_effect=[
                ("token1_jwt", datetime.utcnow()),
                ("token2_jwt", datetime.utcnow()),
                ("token3_jwt", datetime.utcnow()),
            ]
        ):
            result1 = await token_service.generate_auto_token(username, "token1")
            result2 = await token_service.generate_auto_token(username, "token2")
            result3 = await token_service.generate_auto_token(username, "token3")
            
            assert result1["token_name"] == "token1"
            assert result2["token_name"] == "token2"
            assert result3["token_name"] == "token3"
    
    def test_uuid_consistency_across_instances(self):
        """Test that UUID generation is consistent across TokenService instances"""
        service1 = TokenService()
        service2 = TokenService()
        
        username = "test_consistency"
        uuid1 = service1.get_consumer_uuid(username)
        uuid2 = service2.get_consumer_uuid(username)
        
        assert uuid1 == uuid2
    
    @pytest.mark.asyncio
    async def test_error_propagation_from_kong_service(self, token_service):
        """Test that errors from KongService propagate correctly"""
        username = "error_user"
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            side_effect=Exception("Kong connection failed")
        ):
            with pytest.raises(Exception, match="Kong connection failed"):
                await token_service.create_consumer_with_token(username)
    
    @pytest.mark.asyncio
    async def test_error_propagation_from_jwt_service(self, token_service):
        """Test that errors from JWTService propagate correctly"""
        username = "test_user"
        consumer_data = {"id": "consumer_err", "username": username}
        jwt_credentials = {"id": "jwt_err", "key": "token_err"}
        secret = "secret"
        
        with patch.object(
            token_service.kong_service, "get_or_create_consumer",
            return_value=(consumer_data, False)
        ), patch.object(
            token_service.kong_service, "create_jwt_credentials",
            return_value=(jwt_credentials, secret, "token_err")
        ), patch.object(
            token_service.jwt_service, "generate_jwt_token",
            side_effect=Exception("JWT encoding failed")
        ):
            with pytest.raises(Exception, match="JWT encoding failed"):
                await token_service.generate_auto_token(username, "token_err")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
