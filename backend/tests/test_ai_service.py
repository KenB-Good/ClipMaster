import sys
import types
import pytest
from datetime import datetime

# Provide dummy heavy modules before importing ai_service
sys.modules.setdefault(
    "torch",
    types.SimpleNamespace(cuda=types.SimpleNamespace(is_available=lambda: False)),
)
sys.modules.setdefault(
    "whisper",
    types.SimpleNamespace(load_model=lambda *a, **k: types.SimpleNamespace(transcribe=lambda p: {"text": "dummy"})),
)
sys.modules.setdefault("numpy", types.ModuleType("numpy"))

from app.services import ai_service
from app.models.video import Video, VideoUpdate, VideoStatus, VideoSource

class DummyVideoService:
    def __init__(self, db):
        self.store = db
    async def get_video(self, vid):
        return self.store.get(vid)
    async def update_video(self, vid, update: VideoUpdate):
        video = self.store.get(vid)
        if not video:
            return None
        data = update.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(video, k, v)
        return video

class DummyTaskService:
    def __init__(self, db):
        self.updates = []
    async def update_task(self, tid, update):
        self.updates.append((tid, update))
        return None

@pytest.fixture
def monkeypatched_ai(monkeypatch):
    monkeypatch.setattr(ai_service, "VideoService", DummyVideoService)
    monkeypatch.setattr(ai_service, "TaskService", DummyTaskService)
    async def fake_load(self):
        self.whisper_model = types.SimpleNamespace(transcribe=lambda p: {"text": "hello"})
    monkeypatch.setattr(ai_service.AIService, "load_whisper_model", fake_load)
    async def fake_extract(self, p):
        return p
    monkeypatch.setattr(ai_service.AIService, "_extract_audio", fake_extract)
    return ai_service.AIService()

@pytest.mark.asyncio
async def test_transcribe_success(monkeypatched_ai):
    store = {
        "v1": Video(
            id="v1",
            filename="f.mp4",
            original_filename="f.mp4",
            file_size=1,
            format="mp4",
            resolution="720p",
            source=VideoSource.UPLOAD,
            file_path="/tmp/f.mp4",
            status=VideoStatus.UPLOADED,
            uploaded_at=datetime.utcnow(),
        )
    }
    result = await monkeypatched_ai.transcribe_video("v1", "t1", store)
    assert result == "hello"

@pytest.mark.asyncio
async def test_transcribe_missing_video(monkeypatched_ai):
    store = {}
    res = await monkeypatched_ai.transcribe_video("missing", "t2", store)
    assert res is None


