import os
import sys
import asyncio
from datetime import datetime
import types

import pytest

# Ensure project root is on sys.path so `import app` works when running from repo root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text="", raise_http=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text
        self._raise_http = raise_http

    def json(self):
        return self._json

    def raise_for_status(self):
        if self._raise_http:
            raise self._raise_http


class HTTPStatusError(Exception):
    def __init__(self, status_code, text=""):
        self.response = types.SimpleNamespace(status_code=status_code, text=text)


class FakeAsyncClient:
    def __init__(self, flows):
        # flows is a dict mapping (method, url) -> list of FakeResponse
        self.flows = flows

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, **kwargs):
        return self._next("GET", url)

    async def post(self, url, **kwargs):
        return self._next("POST", url)

    def _next(self, method, url):
        key = (method, url)
        queue = self.flows.get(key, [])
        if not queue:
            return FakeResponse(status_code=404, json_data={}, text="Not mocked")
        return queue.pop(0)


@pytest.fixture(autouse=True)
def _isolate_settings_env(monkeypatch):
    # Ensure predictable config without relying on host env
    monkeypatch.setenv("KONG_ADMIN_URL", "http://kong-admin:8001")
    monkeypatch.setenv("JWT_EXPIRATION_SECONDS", "3600")


def _import_app():
    # Late import to apply monkeypatches first
    from app import main as app_main
    return app_main


def test_create_consumer_creates_when_absent(monkeypatch):
    app_main = _import_app()

    username = "user-a"
    kong = "http://kong-admin:8001"

    flows = {
        ("GET", f"{kong}/consumers/{username}"): [FakeResponse(status_code=404, json_data={})],
        ("POST", f"{kong}/consumers/"): [
            FakeResponse(status_code=201, json_data={"username": username, "id": "cid-1"})
        ],
        ("POST", f"{kong}/consumers/{username}/jwt"): [
            FakeResponse(status_code=201, json_data={"id": "jwt-1"})
        ],
    }

    fake_client = FakeAsyncClient(flows)
    monkeypatch.setattr(app_main, "httpx", types.SimpleNamespace(AsyncClient=lambda: fake_client))

    # Build request model
    req = app_main.ConsumerRequest(username=username)

    # Run handler
    result = asyncio.get_event_loop().run_until_complete(app_main.create_consumer(req))

    assert result.username == username
    assert result.token
    assert result.expires_at > datetime.utcnow()


def test_create_consumer_duplicate_consumer_retrieved(monkeypatch):
    app_main = _import_app()

    username = "user-b"
    kong = "http://kong-admin:8001"

    # First try create -> 409, then GET existing, then create jwt
    conflict_error = HTTPStatusError(409, text="exists")
    flows = {
        ("GET", f"{kong}/consumers/{username}"): [
            FakeResponse(status_code=200, json_data={"username": username, "id": "cid-2"})
        ],
        ("POST", f"{kong}/consumers/"): [
            FakeResponse(status_code=409, json_data={}, raise_http=conflict_error)
        ],
        ("POST", f"{kong}/consumers/{username}/jwt"): [
            FakeResponse(status_code=201, json_data={"id": "jwt-2"})
        ],
    }

    fake_client = FakeAsyncClient(flows)
    monkeypatch.setattr(app_main, "httpx", types.SimpleNamespace(AsyncClient=lambda: fake_client))

    req = app_main.ConsumerRequest(username=username)
    result = asyncio.get_event_loop().run_until_complete(app_main.create_consumer(req))

    assert result.username == username
    assert result.token


def test_generate_token_auto_retries_on_duplicate_jwt_name(monkeypatch):
    app_main = _import_app()

    username = "dup"
    kong = "http://kong-admin:8001"

    # User dependency: return a simple CasdoorUser stub
    class StubUser:
        def __init__(self, name):
            self.name = name

    async def fake_dep():
        return StubUser(username)

    monkeypatch.setattr(app_main, "get_current_user", lambda: fake_dep())

    # 1) GET consumer -> 200 existing
    # 2) POST jwt first -> raise 409
    # 3) POST jwt retry -> success with id
    conflict_error = HTTPStatusError(409, text="duplicate key")
    flows = {
        ("GET", f"{kong}/consumers/{username}"): [
            FakeResponse(status_code=200, json_data={"username": username, "id": "cid-3"})
        ],
        ("POST", f"{kong}/consumers/{username}/jwt"): [
            FakeResponse(status_code=409, json_data={}, raise_http=conflict_error),
            FakeResponse(status_code=201, json_data={"id": "jwt-3"}),
        ],
    }

    fake_client = FakeAsyncClient(flows)
    monkeypatch.setattr(app_main, "httpx", types.SimpleNamespace(AsyncClient=lambda: fake_client))

    # Call endpoint
    result = asyncio.get_event_loop().run_until_complete(
        app_main.generate_token_auto(request=None, current_user=StubUser(username))
    )

    assert result.token
    assert result.token_id == "jwt-3"
    assert result.expires_at > datetime.utcnow()


def test_auto_generate_consumer_duplicate_jwt_name(monkeypatch):
    app_main = _import_app()

    username = "auto-user"
    kong = "http://kong-admin:8001"

    class StubUser:
        def __init__(self, name):
            self.name = name

    conflict_error = HTTPStatusError(409, text="duplicate")
    flows = {
        ("GET", f"{kong}/consumers/{username}"): [
            FakeResponse(status_code=200, json_data={"username": username})
        ],
        ("POST", f"{kong}/consumers/{username}/jwt"): [
            FakeResponse(status_code=409, json_data={}, raise_http=conflict_error),
            FakeResponse(status_code=201, json_data={"id": "jwt-4"}),
        ],
    }

    fake_client = FakeAsyncClient(flows)
    monkeypatch.setattr(app_main, "httpx", types.SimpleNamespace(AsyncClient=lambda: fake_client))

    result = asyncio.get_event_loop().run_until_complete(
        app_main.auto_generate_consumer(current_user=StubUser(username))
    )

    assert result.username == username
    assert result.token_id == "jwt-4"
    assert result.consumer_created in (True, False)


def test_list_consumers_success(monkeypatch):
    app_main = _import_app()

    class StubUser:
        def __init__(self, name):
            self.name = name

    flows = {
        ("GET", f"http://kong-admin:8001/consumers/"): [
            FakeResponse(status_code=200, json_data=[{"username": "a"}, {"username": "b"}])
        ]
    }
    fake_client = FakeAsyncClient(flows)
    monkeypatch.setattr(app_main, "httpx", types.SimpleNamespace(AsyncClient=lambda: fake_client))

    out = asyncio.get_event_loop().run_until_complete(
        app_main.list_consumers(current_user=StubUser("any"))
    )
    assert isinstance(out, list)
    assert len(out) == 2


