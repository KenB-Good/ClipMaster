import asyncio
from datetime import datetime
import pytest

from app.twitch.stream_monitor import StreamMonitor
from app.models.twitch import TwitchIntegration
from app.twitch.client import TwitchAPIClient
from app.services import twitch_service


class DummyService:
    def __init__(self, db):
        self.db = db
        self.updated = []

    async def get_integration(self, integration_id: str) -> TwitchIntegration:
        return TwitchIntegration(
            id=integration_id,
            username="tester",
            user_id="user123",
            access_token="",  # not used
            refresh_token="",
            is_monitoring=False,
            auto_capture=False,
            chat_monitoring=False,
            last_stream_id=None,
            last_stream_title=None,
            last_stream_game=None,
            connected_at=datetime.utcnow(),
            last_used_at=datetime.utcnow(),
        )

    async def update_integration(self, integration_id: str, data):
        self.updated.append((integration_id, data))
        return None


@pytest.mark.asyncio
async def test_monitoring_loop_updates_db(monkeypatch):
    service = DummyService(None)
    monkeypatch.setattr(twitch_service, "TwitchService", lambda db: service)

    async def fake_stream_info(self, user_id):
        return {
            "is_live": True,
            "stream_id": "abc",
            "title": "Hello",
            "game_name": "Game",
            "viewer_count": 10,
        }

    monkeypatch.setattr(TwitchAPIClient, "get_stream_info", fake_stream_info)

    monitor = StreamMonitor("integration1", db=None)

    async def fake_sleep(seconds):
        monitor.is_monitoring = False
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(StreamMonitor, "_check_highlight_triggers", lambda self: asyncio.sleep(0))

    monitor.is_monitoring = True
    integration = await service.get_integration("integration1")
    await monitor._monitoring_loop(integration, auto_capture=False)

    assert service.updated
    upd = service.updated[0][1]
    assert upd["last_stream_id"] == "abc"
    assert upd["last_stream_title"] == "Hello"
    assert upd["last_stream_game"] == "Game"
