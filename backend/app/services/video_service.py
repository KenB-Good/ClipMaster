
"""
Video service for database operations
"""
import os
from typing import List, Optional
from datetime import datetime
from databases import Database

from app.models.video import VideoCreate, VideoUpdate, Video, VideoStatus, Highlight, Clip
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, db: Database):
        self.db = db

    async def create_video(self, video_data: VideoCreate, file_path: str) -> Video:
        """Create a new video record"""
        query = """
        INSERT INTO videos (id, filename, original_filename, file_path, file_size, format, 
                           resolution, source, twitch_stream_id, twitch_title, twitch_game, 
                           uploaded_at, status)
        VALUES (:id, :filename, :original_filename, :file_path, :file_size, :format,
                :resolution, :source, :twitch_stream_id, :twitch_title, :twitch_game,
                :uploaded_at, :status)
        RETURNING *
        """
        
        import uuid
        video_id = str(uuid.uuid4())
        
        values = {
            "id": video_id,
            "filename": video_data.filename,
            "original_filename": video_data.original_filename,
            "file_path": file_path,
            "file_size": video_data.file_size,
            "format": video_data.format,
            "resolution": video_data.resolution,
            "source": video_data.source,
            "twitch_stream_id": video_data.twitch_stream_id,
            "twitch_title": video_data.twitch_title,
            "twitch_game": video_data.twitch_game,
            "uploaded_at": datetime.utcnow(),
            "status": VideoStatus.UPLOADED
        }
        
        result = await self.db.fetch_one(query, values)
        return Video(**result) if result else None

    async def get_video(self, video_id: str) -> Optional[Video]:
        """Get video by ID"""
        query = "SELECT * FROM videos WHERE id = :video_id"
        result = await self.db.fetch_one(query, {"video_id": video_id})
        return Video(**result) if result else None

    async def get_videos(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[VideoStatus] = None
    ) -> List[Video]:
        """Get list of videos"""
        where_clause = ""
        values = {"skip": skip, "limit": limit}
        
        if status:
            where_clause = "WHERE status = :status"
            values["status"] = status
        
        query = f"""
        SELECT * FROM videos 
        {where_clause}
        ORDER BY uploaded_at DESC 
        OFFSET :skip LIMIT :limit
        """
        
        results = await self.db.fetch_all(query, values)
        return [Video(**result) for result in results]

    async def update_video(self, video_id: str, video_update: VideoUpdate) -> Optional[Video]:
        """Update video"""
        # Build dynamic update query
        set_clauses = []
        values = {"video_id": video_id}
        
        if video_update.status is not None:
            set_clauses.append("status = :status")
            values["status"] = video_update.status
            
        if video_update.transcription is not None:
            set_clauses.append("transcription = :transcription")
            values["transcription"] = video_update.transcription
            
        if video_update.processed_at is not None:
            set_clauses.append("processed_at = :processed_at")
            values["processed_at"] = video_update.processed_at
        
        if not set_clauses:
            return await self.get_video(video_id)
        
        query = f"""
        UPDATE videos 
        SET {', '.join(set_clauses)}
        WHERE id = :video_id
        RETURNING *
        """
        
        result = await self.db.fetch_one(query, values)
        return Video(**result) if result else None

    async def delete_video(self, video_id: str) -> bool:
        """Delete video"""
        query = "DELETE FROM videos WHERE id = :video_id"
        result = await self.db.execute(query, {"video_id": video_id})
        return result > 0

    async def get_video_highlights(self, video_id: str) -> List[Highlight]:
        """Get highlights for a video"""
        query = """
        SELECT * FROM highlights 
        WHERE video_id = :video_id 
        ORDER BY start_time ASC
        """
        results = await self.db.fetch_all(query, {"video_id": video_id})
        return [Highlight(**result) for result in results]

    async def get_video_clips(self, video_id: str) -> List[Clip]:
        """Get clips for a video"""
        query = """
        SELECT * FROM clips 
        WHERE video_id = :video_id 
        ORDER BY created_at DESC
        """
        results = await self.db.fetch_all(query, {"video_id": video_id})
        return [Clip(**result) for result in results]

    async def get_videos_by_status(self, status: VideoStatus) -> List[Video]:
        """Get videos by status"""
        query = "SELECT * FROM videos WHERE status = :status ORDER BY uploaded_at DESC"
        results = await self.db.fetch_all(query, {"status": status})
        return [Video(**result) for result in results]
