
"""
File service for file operations and management
"""
import os
import shutil
import aiofiles
from typing import List, Dict, Any, Optional
from databases import Database

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.clips_dir = settings.CLIPS_DIR
        self.temp_dir = settings.TEMP_DIR

    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to storage"""
        file_path = os.path.join(self.upload_dir, filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return file_path

    async def delete_video_files(self, video_id: str) -> Dict[str, Any]:
        """Delete all files associated with a video"""
        deleted_files = []
        errors = []
        
        try:
            # Get video file path from database (would need db connection)
            # For now, scan directories for files with video_id
            
            # Delete from upload directory
            for filename in os.listdir(self.upload_dir):
                if video_id in filename:
                    file_path = os.path.join(self.upload_dir, filename)
                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                    except Exception as e:
                        errors.append(f"Error deleting {file_path}: {str(e)}")
            
            # Delete from clips directory
            for filename in os.listdir(self.clips_dir):
                if video_id in filename:
                    file_path = os.path.join(self.clips_dir, filename)
                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                    except Exception as e:
                        errors.append(f"Error deleting {file_path}: {str(e)}")
            
            # Delete from temp directory
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    if video_id in filename:
                        file_path = os.path.join(self.temp_dir, filename)
                        try:
                            os.remove(file_path)
                            deleted_files.append(file_path)
                        except Exception as e:
                            errors.append(f"Error deleting {file_path}: {str(e)}")
                            
        except Exception as e:
            logger.error(f"Error in delete_video_files: {e}")
            errors.append(str(e))
        
        return {
            "deleted_files": deleted_files,
            "errors": errors,
            "count": len(deleted_files)
        }

    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        if not os.path.exists(file_path):
            return None
        
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "is_file": os.path.isfile(file_path),
                "permissions": oct(stat.st_mode)[-3:]
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

    async def move_file(self, source: str, destination: str) -> bool:
        """Move file from source to destination"""
        try:
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            return True
        except Exception as e:
            logger.error(f"Error moving file from {source} to {destination}: {e}")
            return False

    async def copy_file(self, source: str, destination: str) -> bool:
        """Copy file from source to destination"""
        try:
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            logger.error(f"Error copying file from {source} to {destination}: {e}")
            return False

    async def cleanup_temp_files(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up temporary files older than max_age_hours"""
        import time
        
        deleted_files = []
        errors = []
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    try:
                        file_age = current_time - os.path.getctime(file_path)
                        if file_age > max_age_seconds:
                            os.remove(file_path)
                            deleted_files.append(file_path)
                    except Exception as e:
                        errors.append(f"Error processing {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error in cleanup_temp_files: {e}")
            errors.append(str(e))
        
        return {
            "deleted_files": deleted_files,
            "errors": errors,
            "count": len(deleted_files)
        }

    def get_available_space(self) -> Dict[str, int]:
        """Get available space in storage directories"""
        result = {}
        
        for name, path in [
            ("upload", self.upload_dir),
            ("clips", self.clips_dir), 
            ("temp", self.temp_dir)
        ]:
            try:
                total, used, free = shutil.disk_usage(path)
                result[name] = {
                    "total": total,
                    "used": used,
                    "free": free
                }
            except Exception as e:
                logger.error(f"Error getting disk usage for {path}: {e}")
                result[name] = {"error": str(e)}
        
        return result

    async def validate_video_file(self, file_path: str) -> Dict[str, Any]:
        """Validate video file format and properties"""
        try:
            import cv2
            
            # Basic file existence check
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File does not exist"}
            
            # Try to open with OpenCV
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return {"valid": False, "error": "Cannot open video file"}
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                "valid": True,
                "properties": {
                    "duration": duration,
                    "fps": fps,
                    "frame_count": frame_count,
                    "width": width,
                    "height": height,
                    "resolution": f"{width}x{height}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating video file {file_path}: {e}")
            return {"valid": False, "error": str(e)}
