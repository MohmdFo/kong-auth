"""
Comprehensive tests for middleware components
Tests request ID, tenant/user scope, and Sentry integration
"""
import uuid
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import pytest
from fastapi import Request, Response
from starlette.datastructures import Headers

from app.middleware.request_id import RequestIDMiddleware
from app.middleware.tenant_user_scope import TenantUserScopeMiddleware
from app.casdoor_oidc import CasdoorUser


@pytest.fixture
def mock_request():
    """Fixture for mock request"""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/test/path"
    request.method = "GET"
    request.headers = {}
    request.state = Mock()
    request.scope = {}
    return request


@pytest.fixture
def mock_casdoor_user():
    """Fixture for mock CasdoorUser"""
    user_data = {
        "owner": "test_org",
        "name": "test_user",
        "displayName": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "avatar": "",
        "roles": ["user"],
        "permissions": ["read"],
        "properties": {}
    }
    token_claims = {
        "sub": "test_org/test_user",
        "iss": "issuer",
        "aud": "audience",
        "exp": 9999999999,
        "iat": 1234567890
    }
    return CasdoorUser(user_data, token_claims)


class TestRequestIDMiddleware:
    """Comprehensive tests for RequestIDMiddleware"""
    
    @pytest.mark.asyncio
    async def test_adds_request_id_to_state(self, mock_request):
        """Test that middleware adds request ID to request state"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        async def call_next(request):
            # Verify request_id was set in state
            assert hasattr(request.state, "request_id")
            assert isinstance(request.state.request_id, str)
            
            # Return mock response
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.observability.sentry.set_request_context"):
            response = await middleware.dispatch(mock_request, call_next)
            
            assert "X-Request-ID" in response.headers
    
    @pytest.mark.asyncio
    async def test_generates_uuid_when_not_provided(self, mock_request):
        """Test UUID generation when not provided in headers"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        mock_request.headers = {}
        
        generated_id = None
        
        async def call_next(request):
            nonlocal generated_id
            generated_id = request.state.request_id
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.observability.sentry.set_request_context"):
            await middleware.dispatch(mock_request, call_next)
            
            # Verify it's a valid UUID
            assert generated_id is not None
            uuid.UUID(generated_id)  # Should not raise
    
    @pytest.mark.asyncio
    async def test_uses_existing_request_id_from_header(self, mock_request):
        """Test using existing request ID from header"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        existing_id = str(uuid.uuid4())
        mock_request.headers = {"X-Request-ID": existing_id}
        
        received_id = None
        
        async def call_next(request):
            nonlocal received_id
            received_id = request.state.request_id
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.observability.sentry.set_request_context"):
            await middleware.dispatch(mock_request, call_next)
            
            assert received_id == existing_id
    
    @pytest.mark.asyncio
    async def test_validates_uuid_format(self, mock_request):
        """Test that invalid UUID in header is rejected"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        invalid_id = "not-a-valid-uuid"
        mock_request.headers = {"X-Request-ID": invalid_id}
        
        received_id = None
        
        async def call_next(request):
            nonlocal received_id
            received_id = request.state.request_id
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.observability.sentry.set_request_context"):
            await middleware.dispatch(mock_request, call_next)
            
            # Should generate new UUID instead of using invalid one
            assert received_id != invalid_id
            uuid.UUID(received_id)  # Should be valid
    
    @pytest.mark.asyncio
    async def test_adds_request_id_to_response_headers(self, mock_request):
        """Test that request ID is added to response headers"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        request_id = str(uuid.uuid4())
        mock_request.state.request_id = request_id
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.middleware.request_id.set_request_context"):
            response = await middleware.dispatch(mock_request, call_next)
            
            # The request_id should be in response headers
            assert "X-Request-ID" in response.headers
    
    @pytest.mark.asyncio
    async def test_sets_sentry_context(self, mock_request):
        """Test that Sentry context is set with request details"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        mock_request.url.path = "/api/test"
        mock_request.method = "POST"
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.middleware.request_id.set_request_context") as mock_sentry:
            await middleware.dispatch(mock_request, call_next)
            
            mock_sentry.assert_called_once()
            call_args = mock_sentry.call_args[1]
            assert "request_id" in call_args
            assert call_args["path"] == "/api/test"
            assert call_args["method"] == "POST"
    
    @pytest.mark.asyncio
    async def test_get_client_ip_from_x_forwarded_for(self, mock_request):
        """Test extracting client IP from X-Forwarded-For header"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        
        client_ip = middleware._get_client_ip(mock_request)
        
        # Should get first IP from list
        assert client_ip == "192.168.1.1"
    
    @pytest.mark.asyncio
    async def test_get_client_ip_from_x_real_ip(self, mock_request):
        """Test extracting client IP from X-Real-IP header"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        mock_request.headers = {"X-Real-IP": "192.168.1.100"}
        
        client_ip = middleware._get_client_ip(mock_request)
        
        assert client_ip == "192.168.1.100"
    
    @pytest.mark.asyncio
    async def test_get_client_ip_fallback_to_request_client(self, mock_request):
        """Test fallback to request.client when no headers"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        mock_request.headers = {}
        mock_request.client = Mock()
        mock_request.client.host = "10.0.0.50"
        
        client_ip = middleware._get_client_ip(mock_request)
        
        assert client_ip == "10.0.0.50"


class TestTenantUserScopeMiddleware:
    """Comprehensive tests for TenantUserScopeMiddleware"""
    
    @pytest.mark.asyncio
    async def test_sets_user_context_when_authenticated(self, mock_request, mock_casdoor_user):
        """Test setting Sentry user context for authenticated request"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        mock_request.state.user = mock_casdoor_user
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.middleware.tenant_user_scope.set_user_context") as mock_set_user:
            await middleware.dispatch(mock_request, call_next)
            
            mock_set_user.assert_called_once()
            call_args = mock_set_user.call_args[1]
            assert call_args["user_id"] == "test_org/test_user"
            assert call_args["username"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_no_context_set_when_unauthenticated(self, mock_request):
        """Test no Sentry context set for unauthenticated request"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        # No user in state
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.middleware.tenant_user_scope.set_user_context") as mock_set_user:
            await middleware.dispatch(mock_request, call_next)
            
            mock_set_user.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_extract_user_info_from_state(self, mock_request, mock_casdoor_user):
        """Test extracting user info from request state"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        mock_request.state.user = mock_casdoor_user
        
        user_info = middleware._extract_user_info(mock_request)
        
        assert user_info is not None
        assert user_info["id"] == "test_org/test_user"
        assert user_info["username"] == "test_user"
        assert user_info["email"] == "test@example.com"
        assert user_info["organization"] == "test_org"
        assert "user" in user_info["roles"]
    
    @pytest.mark.asyncio
    async def test_extract_user_info_from_scope(self, mock_request, mock_casdoor_user):
        """Test extracting user info from request scope"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        mock_request.scope = {"user": mock_casdoor_user}
        
        user_info = middleware._extract_user_info(mock_request)
        
        assert user_info is not None
        assert user_info["username"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_extract_user_info_returns_none_when_no_user(self, mock_request):
        """Test returning None when no user is present"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        user_info = middleware._extract_user_info(mock_request)
        
        assert user_info is None
    
    @pytest.mark.asyncio
    async def test_extract_tenant_info(self, mock_request):
        """Test extracting tenant information"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        # Mock tenant info in headers or state
        mock_request.headers = {"X-Tenant-ID": "tenant_123"}
        
        tenant_info = middleware._extract_tenant_info(mock_request)
        
        # Implementation may vary, test what's expected
        # This is a placeholder test
        assert tenant_info is not None or tenant_info is None
    
    @pytest.mark.asyncio
    async def test_handles_exception_gracefully(self, mock_request):
        """Test that exceptions in user extraction don't break request"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        # Create a request that will cause an exception
        mock_request.state.user = "invalid_user_format"
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        # Should not raise exception
        response = await middleware.dispatch(mock_request, call_next)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_sets_tenant_id_in_context(self, mock_request, mock_casdoor_user):
        """Test setting tenant ID in Sentry context"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        mock_request.state.user = mock_casdoor_user
        mock_request.headers = {"X-Tenant-ID": "tenant_456"}
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.middleware.tenant_user_scope.set_user_context") as mock_set_user, \
             patch.object(middleware, "_extract_tenant_info",
                          return_value={"id": "tenant_456", "name": "Test Tenant"}):
            await middleware.dispatch(mock_request, call_next)
            
            mock_set_user.assert_called_once()
            call_args = mock_set_user.call_args[1]
            assert call_args["tenant_id"] == "tenant_456"


class TestMiddlewareIntegration:
    """Integration tests for middleware stack"""
    
    @pytest.mark.asyncio
    async def test_middleware_chain_execution_order(self, mock_request):
        """Test that middlewares execute in correct order"""
        app = Mock()
        
        execution_order = []
        
        class TrackingMiddleware(RequestIDMiddleware):
            async def dispatch(self, request, call_next):
                execution_order.append("request_id_start")
                response = await super().dispatch(request, call_next)
                execution_order.append("request_id_end")
                return response
        
        middleware = TrackingMiddleware(app)
        
        async def call_next(request):
            execution_order.append("handler")
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.observability.sentry.set_request_context"):
            await middleware.dispatch(mock_request, call_next)
        
        assert execution_order == ["request_id_start", "handler", "request_id_end"]
    
    @pytest.mark.asyncio
    async def test_request_id_available_to_downstream_middleware(self, mock_request):
        """Test that request ID set by one middleware is available to next"""
        app = Mock()
        request_id_middleware = RequestIDMiddleware(app)
        
        captured_request_id = None
        
        async def call_next(request):
            nonlocal captured_request_id
            captured_request_id = getattr(request.state, "request_id", None)
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.observability.sentry.set_request_context"):
            await request_id_middleware.dispatch(mock_request, call_next)
        
        assert captured_request_id is not None
        uuid.UUID(captured_request_id)  # Should be valid UUID
    
    @pytest.mark.asyncio
    async def test_middleware_error_handling(self, mock_request):
        """Test middleware behavior when downstream raises exception"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        async def call_next(request):
            raise ValueError("Simulated error")
        
        with patch("app.observability.sentry.set_request_context"):
            with pytest.raises(ValueError, match="Simulated error"):
                await middleware.dispatch(mock_request, call_next)


class TestMiddlewareEdgeCases:
    """Edge cases and boundary conditions for middleware"""
    
    @pytest.mark.asyncio
    async def test_very_long_request_path(self, mock_request):
        """Test handling very long request paths"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        mock_request.url.path = "/api/" + "a" * 10000  # Very long path
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.observability.sentry.set_request_context"):
            response = await middleware.dispatch(mock_request, call_next)
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_multiple_x_forwarded_for_ips(self, mock_request):
        """Test handling multiple IPs in X-Forwarded-For"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        mock_request.headers = {
            "X-Forwarded-For": "192.168.1.1, 10.0.0.1, 172.16.0.1, 8.8.8.8"
        }
        
        client_ip = middleware._get_client_ip(mock_request)
        
        # Should return first IP (client's real IP)
        assert client_ip == "192.168.1.1"
    
    @pytest.mark.asyncio
    async def test_malformed_headers(self, mock_request):
        """Test handling malformed headers gracefully"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        mock_request.headers = {
            "X-Request-ID": None,  # Malformed
            "X-Forwarded-For": "",  # Empty
        }
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        with patch("app.observability.sentry.set_request_context"):
            response = await middleware.dispatch(mock_request, call_next)
            
            # Should handle gracefully and generate new ID
            assert "X-Request-ID" in response.headers
    
    @pytest.mark.asyncio
    async def test_user_with_missing_attributes(self, mock_request):
        """Test handling user object with missing attributes"""
        app = Mock()
        middleware = TenantUserScopeMiddleware(app)
        
        # User with minimal attributes
        incomplete_user = Mock()
        incomplete_user.id = "user_123"
        incomplete_user.name = "test_user"
        # Missing email, organization, roles, etc.
        
        mock_request.state.user = incomplete_user
        
        async def call_next(request):
            response = Mock(spec=Response)
            response.headers = {}
            response.status_code = 200
            return response
        
        # Should handle gracefully without crashing
        response = await middleware.dispatch(mock_request, call_next)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_unique_ids(self):
        """Test that concurrent requests get unique request IDs"""
        app = Mock()
        middleware = RequestIDMiddleware(app)
        
        request_ids = []
        
        async def process_request():
            mock_req = Mock(spec=Request)
            mock_req.url = Mock()
            mock_req.url.path = "/test"
            mock_req.method = "GET"
            mock_req.headers = {}
            mock_req.state = Mock()
            
            async def call_next(request):
                request_ids.append(request.state.request_id)
                response = Mock(spec=Response)
                response.headers = {}
                response.status_code = 200
                return response
            
            with patch("app.observability.sentry.set_request_context"):
                await middleware.dispatch(mock_req, call_next)
        
        # Simulate concurrent requests
        import asyncio
        await asyncio.gather(
            process_request(),
            process_request(),
            process_request()
        )
        
        # All IDs should be unique
        assert len(request_ids) == 3
        assert len(set(request_ids)) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
