import pytest
from datetime import datetime
from app.services.video_service import VideoService
from app.models.video import VideoCreate, VideoUpdate, VideoStatus, VideoSource

@pytest.mark.asyncio
async def test_video_crud_flow(db):
    service = VideoService(db)
    data = VideoCreate(
        filename="test.mp4",
        original_filename="orig.mp4",
        file_size=100,
        format="mp4",
        resolution="720p",
        source=VideoSource.UPLOAD,
    )
    video = await service.create_video(data, "/tmp/test.mp4")
    assert video.filename == "test.mp4"

    fetched = await service.get_video(video.id)
    assert fetched is not None and fetched.id == video.id


    updated = await service.update_video(video.id, VideoUpdate(status=VideoStatus.PROCESSED))
    assert updated.status == VideoStatus.PROCESSED

    await service.delete_video(video.id)
    assert await service.get_video(video.id) is None

@pytest.mark.asyncio
async def test_update_no_fields(db):
    service = VideoService(db)
    data = VideoCreate(
        filename="a.mp4",
        original_filename="a.mp4",
        file_size=1,
        format="mp4",
        resolution=None,
        source=VideoSource.UPLOAD,
    )
    video = await service.create_video(data, "/tmp/a.mp4")
    # Updating with no fields should return original
    res = await service.update_video(video.id, VideoUpdate())
    assert res.id == video.id

@pytest.mark.asyncio
async def test_get_video_missing(db):
    service = VideoService(db)
    assert await service.get_video("missing") is None
