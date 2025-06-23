import pytest
from datetime import datetime
from app.services import twitch_service
from app.models.twitch import TwitchIntegrationCreate

class DummyClient:
    def __init__(self):
        self.refreshed = []
    async def refresh_access_token(self, token):
        self.refreshed.append(token)
        return {"access_token": "newA", "refresh_token": "newR"}

@pytest.fixture
def service(monkeypatch, db):
    monkeypatch.setattr(twitch_service, "TwitchAPIClient", DummyClient)
    return twitch_service.TwitchService(db)

@pytest.mark.asyncio
async def test_create_and_get(service):
    data = TwitchIntegrationCreate(access_token="aa", refresh_token="rr", username="u", user_id="1")
    integ = await service.create_integration(data)
    assert integ.username == "u"
    fetched = await service.get_integration(integ.id)
    assert fetched.username == "u"

@pytest.mark.asyncio
async def test_refresh_token(service):
    data = TwitchIntegrationCreate(access_token="a", refresh_token="r", username="u2", user_id="2")
    integ = await service.create_integration(data)
    ok = await service.refresh_token(integ.id)
    assert ok

@pytest.mark.asyncio
async def test_refresh_token_missing(service):
    assert await service.refresh_token("missing") is False

