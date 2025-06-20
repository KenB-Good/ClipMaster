import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime

from app.api.endpoints.twitch import router, get_db
from app.services.twitch_service import TwitchService
from app.twitch.client import TwitchAPIClient
from app.models.twitch import TwitchIntegration, TwitchIntegrationCreate

class DummyDB:
    pass

@pytest.fixture
def app_client(monkeypatch):
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/twitch")

    async def override_get_db():
        yield DummyDB()

    app.dependency_overrides[get_db] = override_get_db

    # Mock Twitch API client methods
    async def fake_exchange(self, code):
        assert code == "testcode"
        return {"access_token": "AA", "refresh_token": "RR"}

    async def fake_user_info(self, token):
        assert token == "AA"
        return {"id": "user123", "login": "tester"}

    monkeypatch.setattr(TwitchAPIClient, "exchange_code_for_token", fake_exchange)
    monkeypatch.setattr(TwitchAPIClient, "get_user_info", fake_user_info)

    created = {}

    async def fake_create(self, data: TwitchIntegrationCreate):
        created.update(data.dict())
        return TwitchIntegration(
            id="integration1",
            username=data.username,
            user_id=data.user_id,
            access_token=data.access_token,
            refresh_token=data.refresh_token,
            is_monitoring=data.is_monitoring,
            auto_capture=data.auto_capture,
            chat_monitoring=data.chat_monitoring,
            last_stream_id=None,
            last_stream_title=None,
            last_stream_game=None,
            connected_at=datetime.utcnow(),
            last_used_at=datetime.utcnow(),
        )

    def fake_init(self, db):
        self.db = db
        self.twitch_client = TwitchAPIClient()

    monkeypatch.setattr(TwitchService, "__init__", fake_init)
    monkeypatch.setattr(TwitchService, "create_integration", fake_create)

    with TestClient(app) as client:
        yield client, created


def test_oauth_callback_creates_integration(app_client):
    client, created = app_client
    response = client.post("/api/v1/twitch/auth/callback?code=testcode")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "tester"
    assert created["username"] == "tester"
    assert created["access_token"] == "AA"
