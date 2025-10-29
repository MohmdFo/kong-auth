"""
Comprehensive tests for Casdoor OIDC authentication
Tests token verification, user extraction, authorization, and edge cases
"""
import base64
import jwt as pyjwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import pytest
from fastapi import HTTPException

from app.casdoor_oidc import (
    CasdoorUser,
    CasdoorOIDC,
    get_current_user,
    get_optional_user,
    require_roles,
    require_permissions,
    require_resource_ownership,
)


@pytest.fixture
def sample_user_data():
    """Fixture for sample user data"""
    return {
        "owner": "organization_sharif",
        "name": "test_user",
        "displayName": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "avatar": "https://example.com/avatar.jpg",
        "roles": ["user", "developer"],
        "permissions": ["read:tokens", "write:tokens"],
        "properties": {"department": "engineering"}
    }


@pytest.fixture
def sample_token_claims():
    """Fixture for sample JWT token claims"""
    return {
        "sub": "organization_sharif/test_user",
        "iss": "https://iam.ai-lab.ir",
        "aud": "kong-auth-service",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "preferred_username": "test_user",
        "email_verified": True,
        "family_name": "User",
        "given_name": "Test"
    }


@pytest.fixture
def casdoor_user(sample_user_data, sample_token_claims):
    """Fixture for CasdoorUser instance"""
    return CasdoorUser(sample_user_data, sample_token_claims)


class TestCasdoorUser:
    """Comprehensive tests for CasdoorUser class"""
    
    def test_user_initialization(self, sample_user_data, sample_token_claims):
        """Test CasdoorUser initialization with valid data"""
        user = CasdoorUser(sample_user_data, sample_token_claims)
        
        assert user.name == "test_user"
        assert user.display_name == "Test User"
        assert user.email == "test@example.com"
        assert user.phone == "+1234567890"
        assert user.organization == "organization_sharif"
        assert "user" in user.roles
        assert "developer" in user.roles
        assert "read:tokens" in user.permissions
    
    def test_user_id_format(self, casdoor_user):
        """Test user ID format (owner/name)"""
        assert casdoor_user.id == "organization_sharif/test_user"
    
    def test_oidc_claims(self, casdoor_user, sample_token_claims):
        """Test OIDC claims are stored correctly"""
        assert casdoor_user.sub == sample_token_claims["sub"]
        assert casdoor_user.iss == sample_token_claims["iss"]
        assert casdoor_user.aud == sample_token_claims["aud"]
        assert casdoor_user.exp == sample_token_claims["exp"]
        assert casdoor_user.iat == sample_token_claims["iat"]
        assert casdoor_user.preferred_username == "test_user"
        assert casdoor_user.email_verified is True
    
    def test_can_access_own_resource(self, casdoor_user):
        """Test user can access their own resources"""
        assert casdoor_user.can_access_resource("test_user") is True
        assert casdoor_user.can_access_resource("organization_sharif/test_user") is True
    
    def test_cannot_access_others_resource(self, casdoor_user):
        """Test user cannot access other users' resources"""
        assert casdoor_user.can_access_resource("other_user") is False
        assert casdoor_user.can_access_resource("organization_sharif/other_user") is False
    
    def test_admin_can_access_all_resources(self, sample_user_data, sample_token_claims):
        """Test admin user can access all resources"""
        sample_user_data["roles"] = ["admin"]
        admin_user = CasdoorUser(sample_user_data, sample_token_claims)
        
        assert admin_user.can_access_resource("any_user") is True
        assert admin_user.can_access_resource("other_user") is True
    
    def test_manage_all_consumers_permission(self, sample_user_data, sample_token_claims):
        """Test manage_all_consumers permission grants access to all"""
        sample_user_data["permissions"] = ["manage_all_consumers"]
        user = CasdoorUser(sample_user_data, sample_token_claims)
        
        assert user.can_access_resource("any_user") is True
    
    def test_to_dict(self, casdoor_user):
        """Test user serialization to dictionary"""
        user_dict = casdoor_user.to_dict()
        
        assert user_dict["id"] == "organization_sharif/test_user"
        assert user_dict["name"] == "test_user"
        assert user_dict["email"] == "test@example.com"
        assert "roles" in user_dict
        assert "permissions" in user_dict
        assert "sub" in user_dict
    
    def test_user_with_missing_optional_fields(self, sample_token_claims):
        """Test user creation with minimal data"""
        minimal_data = {
            "owner": "org",
            "name": "minimal_user",
            "displayName": "",
            "email": "",
            "phone": "",
            "avatar": "",
            "roles": [],
            "permissions": [],
            "properties": {}
        }
        
        user = CasdoorUser(minimal_data, sample_token_claims)
        
        assert user.name == "minimal_user"
        assert user.email == ""
        assert user.roles == []
        assert user.permissions == []
    
    def test_user_with_special_characters_in_name(self, sample_token_claims):
        """Test user with special characters in name"""
        user_data = {
            "owner": "org",
            "name": "user+test@example.com",
            "displayName": "User Test",
            "email": "user+test@example.com",
            "phone": "",
            "avatar": "",
            "roles": ["user"],
            "permissions": [],
            "properties": {}
        }
        
        user = CasdoorUser(user_data, sample_token_claims)
        
        assert user.name == "user+test@example.com"
        assert user.id == "org/user+test@example.com"


class TestCasdoorOIDC:
    """Comprehensive tests for CasdoorOIDC class"""
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, sample_user_data, sample_token_claims):
        """Test successful token verification"""
        oidc = CasdoorOIDC()
        
        # Create a valid JWT token
        secret = "test_secret"
        token = pyjwt.encode(sample_token_claims, secret, algorithm="HS256")
        
        # Mock the JWKS client to avoid external calls
        mock_jwks_client = Mock()
        mock_signing_key = Mock()
        mock_signing_key.key = secret
        mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key
        
        with patch.object(oidc, "jwks_client", mock_jwks_client), \
             patch.object(oidc, "_get_user_info", return_value=sample_user_data), \
             patch("jwt.decode", return_value=sample_token_claims):
            
            user = await oidc.verify_token(token)
            
            assert isinstance(user, CasdoorUser)
            assert user.name == "test_user"
    
    @pytest.mark.asyncio
    async def test_verify_token_expired(self):
        """Test token verification with expired token"""
        oidc = CasdoorOIDC()
        
        expired_claims = {
            "sub": "org/user",
            "iss": "issuer",
            "aud": "audience",
            "exp": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),  # Expired
            "iat": int((datetime.utcnow() - timedelta(hours=2)).timestamp())
        }
        
        secret = "test_secret"
        token = pyjwt.encode(expired_claims, secret, algorithm="HS256")
        
        # Mock the JWKS client
        mock_jwks_client = Mock()
        mock_signing_key = Mock()
        mock_signing_key.key = secret
        mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key
        
        with patch.object(oidc, "jwks_client", mock_jwks_client):
            with pytest.raises(HTTPException) as exc_info:
                await oidc.verify_token(token)
            
            assert exc_info.value.status_code == 401
            # Accept any token-related error message
            assert "token" in exc_info.value.detail.lower() or "invalid" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid_signature(self):
        """Test token verification with invalid signature"""
        oidc = CasdoorOIDC()
        
        claims = {
            "sub": "org/user",
            "iss": "issuer",
            "aud": "audience",
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        }
        
        # Sign with one secret, verify with another
        token = pyjwt.encode(claims, "wrong_secret", algorithm="HS256")
        
        with patch.object(oidc, "_load_certificate_key", return_value="correct_secret"):
            with pytest.raises(HTTPException) as exc_info:
                await oidc.verify_token(token)
            
            assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_verify_token_malformed(self):
        """Test token verification with malformed token"""
        oidc = CasdoorOIDC()
        
        malformed_token = "not.a.valid.jwt.token"
        
        with patch.object(oidc, "_load_certificate_key", return_value="secret"):
            with pytest.raises(HTTPException) as exc_info:
                await oidc.verify_token(malformed_token)
            
            assert exc_info.value.status_code == 401
    
    def test_load_certificate_key_success(self):
        """Test loading certificate key from file"""
        oidc = CasdoorOIDC()
        
        mock_cert = "-----BEGIN CERTIFICATE-----\nMOCK_CERT_DATA\n-----END CERTIFICATE-----"
        
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=mock_cert)):
            
            key = oidc._load_certificate_key()
            
            assert key == mock_cert
    
    def test_load_certificate_key_not_found(self):
        """Test loading certificate when file doesn't exist"""
        oidc = CasdoorOIDC()
        
        with patch("os.path.exists", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                oidc._load_certificate_key()
            
            assert exc_info.value.status_code == 500
            # Check for the generic error message
            assert "loading failed" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_get_user_info_via_sdk(self):
        """Test getting user info via Casdoor SDK"""
        oidc = CasdoorOIDC()
        
        user_data = {
            "owner": "org",
            "name": "sdk_user",
            "displayName": "SDK User",
            "email": "sdk@example.com",
            "phone": "",
            "avatar": "",
            "roles": ["user"],
            "permissions": [],
            "properties": {}
        }
        
        oidc.casdoor = Mock()
        oidc.casdoor.get_user.return_value = user_data
        
        result = await oidc._get_user_info("org/sdk_user")
        
        assert result == user_data
    
    @pytest.mark.asyncio
    async def test_get_user_info_via_api_fallback(self):
        """Test getting user info via API when SDK fails"""
        oidc = CasdoorOIDC()
        
        user_data = {
            "owner": "org",
            "name": "api_user",
            "displayName": "API User",
            "email": "api@example.com",
            "phone": "",
            "avatar": "",
            "roles": ["user"],
            "permissions": [],
            "properties": {}
        }
        
        oidc.casdoor = Mock()
        oidc.casdoor.get_user.side_effect = Exception("SDK error")
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = user_data
            mock_client.get.return_value = mock_response
            
            result = await oidc._get_user_info("org/api_user")
            
            assert result == user_data
    
    @pytest.mark.asyncio
    async def test_get_user_info_fallback_to_basic(self):
        """Test fallback to basic user info when all methods fail"""
        oidc = CasdoorOIDC()
        
        oidc.casdoor = Mock()
        oidc.casdoor.get_user.side_effect = Exception("SDK error")
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 404
            mock_client.get.return_value = mock_response
            
            result = await oidc._get_user_info("org/fallback_user")
            
            # Should return basic user info
            assert result["name"] == "fallback_user"
            assert result["owner"] == oidc.organization
    
    def test_get_authorization_url(self):
        """Test getting authorization URL for OIDC login"""
        oidc = CasdoorOIDC()
        
        oidc.casdoor = Mock()
        oidc.casdoor.get_auth_link.return_value = "https://iam.example.com/login?..."
        
        url = oidc.get_authorization_url("https://app.example.com/callback", "state123")
        
        assert url.startswith("https://")
        oidc.casdoor.get_auth_link.assert_called_once()
    
    def test_get_authorization_url_no_sdk(self):
        """Test getting authorization URL when SDK is not available"""
        oidc = CasdoorOIDC()
        oidc.casdoor = None
        
        with pytest.raises(HTTPException) as exc_info:
            oidc.get_authorization_url("https://app.example.com/callback")
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self):
        """Test exchanging authorization code for tokens"""
        oidc = CasdoorOIDC()
        
        token_response = {
            "access_token": "access_token_here",
            "refresh_token": "refresh_token_here",
            "id_token": "id_token_here",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        
        oidc.casdoor = Mock()
        oidc.casdoor.get_oauth_token.return_value = token_response
        
        result = await oidc.exchange_code_for_token("auth_code_123", "https://app.example.com/callback")
        
        assert result == token_response
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_error(self):
        """Test error handling when code exchange fails"""
        oidc = CasdoorOIDC()
        
        oidc.casdoor = Mock()
        oidc.casdoor.get_oauth_token.side_effect = Exception("Invalid code")
        
        with pytest.raises(HTTPException) as exc_info:
            await oidc.exchange_code_for_token("invalid_code", "https://app.example.com/callback")
        
        assert exc_info.value.status_code == 400


class TestAuthenticationDependencies:
    """Tests for authentication dependencies and decorators"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, sample_user_data, sample_token_claims):
        """Test get_current_user with valid token"""
        mock_credentials = Mock()
        mock_credentials.credentials = "valid_token"
        
        expected_user = CasdoorUser(sample_user_data, sample_token_claims)
        
        with patch("app.casdoor_oidc.CasdoorOIDC.verify_token", return_value=expected_user):
            user = await get_current_user(mock_credentials)
            
            assert isinstance(user, CasdoorUser)
            assert user.name == "test_user"
    
    @pytest.mark.asyncio
    async def test_get_current_user_fallback_to_simple_extraction(self, sample_token_claims):
        """Test fallback to simple token extraction when OIDC fails"""
        mock_credentials = Mock()
        # Create a valid JWT token format
        secret = "test_secret"
        token = pyjwt.encode(sample_token_claims, secret, algorithm="HS256")
        mock_credentials.credentials = token
        
        with patch("app.casdoor_oidc.CasdoorOIDC.verify_token",
                   side_effect=Exception("OIDC failed")), \
             patch("app.token_utils.extract_username_from_token",
                   return_value="fallback_user"):
            
            user = await get_current_user(mock_credentials)
            
            assert isinstance(user, CasdoorUser)
            assert user.name == "fallback_user"
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid_token"
        
        with patch("app.casdoor_oidc.CasdoorOIDC.verify_token",
                   side_effect=HTTPException(status_code=401, detail="Invalid token")), \
             patch("app.token_utils.extract_username_from_token",
                   return_value=None):
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)
            
            assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_optional_user_with_token(self, sample_user_data, sample_token_claims):
        """Test get_optional_user with valid authorization header"""
        expected_user = CasdoorUser(sample_user_data, sample_token_claims)
        
        with patch("app.casdoor_oidc.casdoor_oidc.verify_token", return_value=expected_user):
            user = await get_optional_user("Bearer valid_token")
            
            assert user is not None
            assert user.name == "test_user"
    
    @pytest.mark.asyncio
    async def test_get_optional_user_without_token(self):
        """Test get_optional_user without authorization header"""
        user = await get_optional_user(None)
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_optional_user_invalid_token(self):
        """Test get_optional_user with invalid token"""
        with patch("app.casdoor_oidc.casdoor_oidc.verify_token",
                   side_effect=HTTPException(status_code=401, detail="Invalid")):
            user = await get_optional_user("Bearer invalid_token")
            
            assert user is None
    
    def test_require_roles_decorator_allowed(self, casdoor_user):
        """Test require_roles decorator allows user with correct role"""
        casdoor_user.roles = ["user", "admin"]
        
        checker = require_roles(["admin"])
        result = checker(casdoor_user)
        
        assert result == casdoor_user
    
    def test_require_roles_decorator_denied(self, casdoor_user):
        """Test require_roles decorator denies user without required role"""
        casdoor_user.roles = ["user"]
        
        checker = require_roles(["admin"])
        
        with pytest.raises(HTTPException) as exc_info:
            checker(casdoor_user)
        
        assert exc_info.value.status_code == 403
        assert "Required roles" in exc_info.value.detail
    
    def test_require_permissions_decorator_allowed(self, casdoor_user):
        """Test require_permissions decorator allows user with correct permission"""
        casdoor_user.permissions = ["read:tokens", "write:tokens"]
        
        checker = require_permissions(["read:tokens"])
        result = checker(casdoor_user)
        
        assert result == casdoor_user
    
    def test_require_permissions_decorator_denied(self, casdoor_user):
        """Test require_permissions decorator denies user without required permission"""
        casdoor_user.permissions = ["read:tokens"]
        
        checker = require_permissions(["delete:all"])
        
        with pytest.raises(HTTPException) as exc_info:
            checker(casdoor_user)
        
        assert exc_info.value.status_code == 403
        assert "Required permissions" in exc_info.value.detail


def mock_open(read_data):
    """Helper to mock file open"""
    from unittest.mock import mock_open as original_mock_open
    return original_mock_open(read_data=read_data)


class TestEdgeCases:
    """Edge cases for authentication"""
    
    def test_user_with_empty_roles_and_permissions(self, sample_token_claims):
        """Test user with no roles or permissions"""
        user_data = {
            "owner": "org",
            "name": "limited_user",
            "displayName": "Limited User",
            "email": "limited@example.com",
            "phone": "",
            "avatar": "",
            "roles": [],
            "permissions": [],
            "properties": {}
        }
        
        user = CasdoorUser(user_data, sample_token_claims)
        
        assert user.roles == []
        assert user.permissions == []
        assert user.can_access_resource("other_user") is False
    
    def test_user_with_very_long_name(self, sample_token_claims):
        """Test user with very long name"""
        long_name = "a" * 1000
        user_data = {
            "owner": "org",
            "name": long_name,
            "displayName": "User",
            "email": "user@example.com",
            "phone": "",
            "avatar": "",
            "roles": ["user"],
            "permissions": [],
            "properties": {}
        }
        
        user = CasdoorUser(user_data, sample_token_claims)
        
        assert user.name == long_name
        assert len(user.id) > 1000
    
    @pytest.mark.asyncio
    async def test_token_with_missing_claims(self):
        """Test handling token with missing required claims"""
        oidc = CasdoorOIDC()
        
        incomplete_claims = {
            "sub": "org/user",
            # Missing iss, aud, exp, iat
        }
        
        secret = "secret"
        token = pyjwt.encode(incomplete_claims, secret, algorithm="HS256")
        
        with patch.object(oidc, "_load_certificate_key", return_value=secret):
            with pytest.raises(HTTPException):
                await oidc.verify_token(token)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
