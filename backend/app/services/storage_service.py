
"""
Storage service for file and space management
"""
import os
import shutil
import hashlib
from typing import Dict, Any, List
from datetime import datetime, timedelta
from databases import Database

from app.models.storage import StorageInfo
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, db: Database):
        self.db = db

    async def get_storage_info(self) -> StorageInfo:
        """Get current storage information"""
        # Get disk usage
        total, used, free = shutil.disk_usage(settings.UPLOAD_DIR)
        
        # Get video and clip counts from database
        video_count_query = "SELECT COUNT(*) as count FROM videos"
        video_result = await self.db.fetch_one(video_count_query)
        video_count = video_result['count'] if video_result else 0
        
        clip_count_query = "SELECT COUNT(*) as count FROM clips"
        clip_result = await self.db.fetch_one(clip_count_query)
        clip_count = clip_result['count'] if clip_result else 0
        
        usage_percentage = (used / total) * 100 if total > 0 else 0
        
        return StorageInfo(
            total_space=total,
            used_space=used,
            available_space=free,
            video_count=video_count,
            clip_count=clip_count,
            usage_percentage=usage_percentage
        )

    async def cleanup_storage(self, force: bool = False) -> Dict[str, Any]:
        """Clean up old files based on configuration"""
        if not force and not settings.AUTO_CLEANUP_ENABLED:
            return {"message": "Auto cleanup is disabled", "cleaned_files": 0}
        
        # Get storage info
        storage_info = await self.get_storage_info()
        
        # Check if cleanup is needed
        if not force and storage_info.usage_percentage < (settings.AUTO_CLEANUP_THRESHOLD * 100):
            return {"message": "Storage usage below threshold", "cleaned_files": 0}
        
        # Get old videos
        cutoff_date = datetime.utcnow() - timedelta(days=settings.AUTO_CLEANUP_DAYS)
        
        old_videos_query = """
        SELECT id, filename, file_path FROM videos 
        WHERE uploaded_at < :cutoff_date AND status = 'ARCHIVED'
        """
        old_videos = await self.db.fetch_all(old_videos_query, {"cutoff_date": cutoff_date})
        
        cleaned_files = 0
        cleaned_size = 0
        
        for video in old_videos:
            try:
                # Delete video file
                if os.path.exists(video['file_path']):
                    file_size = os.path.getsize(video['file_path'])
                    os.remove(video['file_path'])
                    cleaned_size += file_size
                    cleaned_files += 1
                
                # Delete associated clips
                clips_query = "SELECT file_path FROM clips WHERE video_id = :video_id"
                clips = await self.db.fetch_all(clips_query, {"video_id": video['id']})
                
                for clip in clips:
                    if os.path.exists(clip['file_path']):
                        clip_size = os.path.getsize(clip['file_path'])
                        os.remove(clip['file_path'])
                        cleaned_size += clip_size
                        cleaned_files += 1
                
                # Delete from database
                await self.db.execute("DELETE FROM videos WHERE id = :video_id", {"video_id": video['id']})
                
            except Exception as e:
                logger.error(f"Error cleaning up video {video['id']}: {e}")
        
        return {
            "message": f"Cleanup completed",
            "cleaned_files": cleaned_files,
            "cleaned_size": cleaned_size,
            "cutoff_date": cutoff_date.isoformat()
        }

    async def optimize_storage(self) -> Dict[str, Any]:
        """Optimize storage by removing duplicate files"""
        duplicates_found = 0
        space_saved = 0
        
        # Find duplicate videos by file size
        duplicate_query = """
        SELECT file_size, array_agg(id) as video_ids 
        FROM videos 
        GROUP BY file_size 
        HAVING COUNT(*) > 1
        """
        
        potential_duplicates = await self.db.fetch_all(duplicate_query)
        
        for group in potential_duplicates:
            video_ids = group['video_ids']
            
            # Get file paths for these videos
            videos_query = "SELECT id, file_path FROM videos WHERE id = ANY(:video_ids)"
            videos = await self.db.fetch_all(videos_query, {"video_ids": video_ids})
            
            # Calculate file hashes to find true duplicates
            file_hashes = {}
            for video in videos:
                if os.path.exists(video['file_path']):
                    file_hash = await self._calculate_file_hash(video['file_path'])
                    if file_hash in file_hashes:
                        # Found duplicate - mark older video for deletion
                        duplicate_id = video['id']
                        try:
                            # Update status instead of deleting immediately
                            await self.db.execute(
                                "UPDATE videos SET status = 'ARCHIVED' WHERE id = :video_id",
                                {"video_id": duplicate_id}
                            )
                            duplicates_found += 1
                            space_saved += group['file_size']
                        except Exception as e:
                            logger.error(f"Error marking duplicate {duplicate_id}: {e}")
                    else:
                        file_hashes[file_hash] = video['id']
        
        return {
            "message": "Storage optimization completed",
            "duplicates_found": duplicates_found,
            "space_saved": space_saved
        }

    async def get_storage_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get storage statistics over time"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = """
        SELECT recorded_at, total_space, used_space, available_space, video_count, clip_count
        FROM storage_stats 
        WHERE recorded_at >= :start_date
        ORDER BY recorded_at ASC
        """
        
        results = await self.db.fetch_all(query, {"start_date": start_date})
        
        return [
            {
                "date": result['recorded_at'].isoformat(),
                "total_space": result['total_space'],
                "used_space": result['used_space'],
                "available_space": result['available_space'],
                "video_count": result['video_count'],
                "clip_count": result['clip_count'],
                "usage_percentage": (result['used_space'] / result['total_space']) * 100
            }
            for result in results
        ]

    async def record_storage_stats(self):
        """Record current storage statistics"""
        storage_info = await self.get_storage_info()
        
        query = """
        INSERT INTO storage_stats (id, total_space, used_space, available_space, 
                                 video_count, clip_count, recorded_at)
        VALUES (:id, :total_space, :used_space, :available_space, 
                :video_count, :clip_count, :recorded_at)
        """
        
        import uuid
        values = {
            "id": str(uuid.uuid4()),
            "total_space": storage_info.total_space,
            "used_space": storage_info.used_space,
            "available_space": storage_info.available_space,
            "video_count": storage_info.video_count,
            "clip_count": storage_info.clip_count,
            "recorded_at": datetime.utcnow()
        }
        
        await self.db.execute(query, values)

    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
