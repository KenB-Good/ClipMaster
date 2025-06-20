"""
System service for ClipMaster
Handles system configuration and monitoring
SECURITY: Fixed SQL injection vulnerabilities with parameterized queries
"""
import logging
import psutil
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from sqlalchemy import text
from ..core.database import database
from ..models.system import SystemConfig, ConfigUpdate, SystemStats

logger = logging.getLogger(__name__)


class SystemService:
    """Service for system management and monitoring"""

    async def get_system_stats(self) -> SystemStats:
        """Get current system statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory usage
            memory = psutil.virtual_memory()
            memory_total = memory.total
            memory_used = memory.used
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_total = disk.total
            disk_used = disk.used
            disk_percent = (disk_used / disk_total) * 100

            # GPU usage (if available)
            gpu_usage = self._get_gpu_usage()

            return SystemStats(
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_total=memory_total,
                memory_used=memory_used,
                memory_percent=memory_percent,
                disk_total=disk_total,
                disk_used=disk_used,
                disk_percent=disk_percent,
                gpu_usage=gpu_usage,
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            raise

    def _get_gpu_usage(self) -> Optional[Dict[str, Any]]:
        """Get GPU usage statistics if available"""
        try:
            import torch

            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_stats = []

                for i in range(gpu_count):
                    memory_allocated = torch.cuda.memory_allocated(i)
                    memory_reserved = torch.cuda.memory_reserved(i)
                    memory_total = torch.cuda.get_device_properties(i).total_memory

                    gpu_stats.append(
                        {
                            "device": i,
                            "name": torch.cuda.get_device_name(i),
                            "memory_allocated": memory_allocated,
                            "memory_reserved": memory_reserved,
                            "memory_total": memory_total,
                            "memory_percent": (memory_allocated / memory_total) * 100,
                        }
                    )

                return {"available": True, "count": gpu_count, "devices": gpu_stats}
        except ImportError:
            pass

        return {"available": False}

    async def get_config(self, key: str) -> Optional[SystemConfig]:
        """Get system configuration value"""
        try:
            # SECURITY FIX: Use parameterized query
            query = text("SELECT * FROM system_configs WHERE key = :key")
            result = await database.fetch_one(query, {"key": key})
            return SystemConfig(**result) if result else None

        except Exception as e:
            logger.error(f"Error getting config {key}: {e}")
            raise

    async def set_config(
        self, key: str, value: str, description: str = None
    ) -> SystemConfig:
        """Set system configuration value"""
        try:
            # SECURITY FIX: Use parameterized query with UPSERT
            query = text(
                """
                INSERT INTO system_configs (key, value, description, updated_at)
                VALUES (:key, :value, :description, :updated_at)
                ON CONFLICT (key) 
                DO UPDATE SET 
                    value = EXCLUDED.value,
                    description = COALESCE(EXCLUDED.description, system_configs.description),
                    updated_at = EXCLUDED.updated_at
                RETURNING *
            """
            )

            values = {
                "key": key,
                "value": value,
                "description": description,
                "updated_at": datetime.utcnow(),
            }

            result = await database.fetch_one(query, values)
            return SystemConfig(**result)

        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            raise

    async def update_config(
        self, key: str, config_update: ConfigUpdate
    ) -> Optional[SystemConfig]:
        """Update system configuration"""
        try:
            # Build update query safely
            set_clauses = []
            values = {"key": key, "updated_at": datetime.utcnow()}

            if config_update.value is not None:
                set_clauses.append("value = :value")
                values["value"] = config_update.value

            if config_update.description is not None:
                set_clauses.append("description = :description")
                values["description"] = config_update.description

            if not set_clauses:
                return await self.get_config(key)

            # Add updated_at to SET clauses
            set_clauses.append("updated_at = :updated_at")

            # SECURITY FIX: Use parameterized query with safe SET clause construction
            query = text(
                f"""
                UPDATE system_configs 
                SET {', '.join(set_clauses)}
                WHERE key = :key
                RETURNING *
            """
            )

            result = await database.fetch_one(query, values)
            return SystemConfig(**result) if result else None

        except Exception as e:
            logger.error(f"Error updating config {key}: {e}")
            raise

    async def delete_config(self, key: str) -> bool:
        """Delete system configuration"""
        try:
            # SECURITY FIX: Use parameterized query
            query = text("DELETE FROM system_configs WHERE key = :key")
            result = await database.execute(query, {"key": key})
            return result > 0

        except Exception as e:
            logger.error(f"Error deleting config {key}: {e}")
            raise

    async def get_all_configs(self) -> List[SystemConfig]:
        """Get all system configurations"""
        try:
            query = text("SELECT * FROM system_configs ORDER BY key")
            results = await database.fetch_all(query)
            return [SystemConfig(**result) for result in results]

        except Exception as e:
            logger.error(f"Error getting all configs: {e}")
            raise

    async def cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary files"""
        try:
            from ..core.config import settings

            temp_dir = settings.TEMP_DIR
            if not os.path.exists(temp_dir):
                return {"cleaned": 0, "size_freed": 0}

            cleaned_count = 0
            size_freed = 0

            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleaned_count += 1
                        size_freed += file_size
                    except OSError as e:
                        logger.warning(
                            f"Could not remove temp file {file_path}: {e}"
                        )

            return {"cleaned": cleaned_count, "size_freed": size_freed}

        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
            raise

    async def check_storage_usage(self) -> Dict[str, Any]:
        """Check storage usage and recommend cleanup if needed"""
        try:
            from ..core.config import settings

            stats = await self.get_system_stats()

            recommendations = []
            if stats.disk_percent > 90:
                recommendations.append("Critical: Disk usage above 90%")
            elif stats.disk_percent > 80:
                recommendations.append("Warning: Disk usage above 80%")

            if stats.memory_percent > 90:
                recommendations.append("Critical: Memory usage above 90%")
            elif stats.memory_percent > 80:
                recommendations.append("Warning: Memory usage above 80%")

            # Check specific directories
            directories = [settings.UPLOAD_DIR, settings.CLIPS_DIR, settings.TEMP_DIR]

            dir_usage = {}
            for directory in directories:
                if os.path.exists(directory):
                    total_size = 0
                    file_count = 0
                    for dirpath, dirnames, filenames in os.walk(directory):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                total_size += os.path.getsize(filepath)
                                file_count += 1
                            except OSError:
                                pass

                    dir_usage[directory] = {"size": total_size, "files": file_count}

            return {
                "disk_usage": stats.disk_percent,
                "memory_usage": stats.memory_percent,
                "recommendations": recommendations,
                "directory_usage": dir_usage,
            }

        except Exception as e:
            logger.error(f"Error checking storage usage: {e}")
            raise
