"""
Video management endpoints
"""

import logging
import os
import uuid
from typing import List, Optional

import aiofiles
from app.core.config import settings
from app.core.database import get_db
from app.models.video import (Video, VideoCreate, VideoSource, VideoStatus,
                              VideoUpdate)
from app.services.file_service import FileService
from app.services.video_service import VideoService
from databases import Database
from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form,
                     HTTPException, UploadFile)
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=dict)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source: str = Form(default="UPLOAD"),
    db: Database = Depends(get_db),
):
    """Upload a video file"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = {".mp4", ".mov", ".avi", ".mkv"}
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        # Save file
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        # Get file info
        file_stats = os.stat(file_path)

        # Create video record
        video_service = VideoService(db)
        video_data = VideoCreate(
            filename=unique_filename,
            original_filename=file.filename,
            file_size=file_stats.st_size,
            format=file_extension.lstrip("."),
            source=VideoSource(source),
        )

        video = await video_service.create_video(video_data, file_path)

        # Start background processing
        background_tasks.add_task(process_video_async, video.id, db)

        return {"message": "Video uploaded successfully", "video_id": video.id}

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Video])
async def get_videos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[VideoStatus] = None,
    db: Database = Depends(get_db),
):
    """Get list of videos"""
    video_service = VideoService(db)
    return await video_service.get_videos(skip=skip, limit=limit, status=status)


@router.get("/{video_id}", response_model=Video)
async def get_video(video_id: str, db: Database = Depends(get_db)):
    """Get video by ID"""
    video_service = VideoService(db)
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.put("/{video_id}", response_model=Video)
async def update_video(
    video_id: str, video_update: VideoUpdate, db: Database = Depends(get_db)
):
    """Update video"""
    video_service = VideoService(db)
    video = await video_service.update_video(video_id, video_update)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.delete("/{video_id}")
async def delete_video(video_id: str, db: Database = Depends(get_db)):
    """Delete video"""
    video_service = VideoService(db)
    file_service = FileService()

    # Get video info first
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Delete files
    await file_service.delete_video_files(video_id)

    # Delete from database
    await video_service.delete_video(video_id)

    return {"message": "Video deleted successfully"}


@router.get("/{video_id}/download")
async def download_video(video_id: str, db: Database = Depends(get_db)):
    """Download original video file"""
    video_service = VideoService(db)
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    file_path = os.path.join(settings.UPLOAD_DIR, video.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        path=file_path,
        filename=video.original_filename,
        media_type="application/octet-stream",
    )


@router.get("/{video_id}/clips")
async def get_video_clips(video_id: str, db: Database = Depends(get_db)):
    """Get clips for a video"""
    video_service = VideoService(db)
    return await video_service.get_video_clips(video_id)


@router.get("/{video_id}/highlights")
async def get_video_highlights(video_id: str, db: Database = Depends(get_db)):
    """Get highlights for a video"""
    video_service = VideoService(db)
    return await video_service.get_video_highlights(video_id)


@router.post("/{video_id}/process")
async def process_video(
    video_id: str, background_tasks: BackgroundTasks, db: Database = Depends(get_db)
):
    """Trigger video processing"""
    video_service = VideoService(db)
    video = await video_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Start background processing
    background_tasks.add_task(process_video_async, video_id, db)

    return {"message": "Processing started", "video_id": video_id}


async def process_video_async(video_id: str, db: Database):
    """Background task for video processing"""
    try:
        from app.services.ai_service import AIService

        ai_service = AIService()
        await ai_service.process_video(video_id, db)
    except Exception as e:
        logger.error(f"Video processing error: {e}")
