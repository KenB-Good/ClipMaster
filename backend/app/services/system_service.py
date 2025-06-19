
"""
System service for configuration and health monitoring
"""
import psutil
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from databases import Database

from app.models.storage import SystemConfig, SystemConfigCreate, SystemConfigUpdate, ConfigType
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SystemService:
    def __init__(self, db: Database):
        self.db = db

    async def get_config(self, key: str) -> Optional[SystemConfig]:
        """Get configuration value by key"""
        query = "SELECT * FROM system_configs WHERE key = :key"
        result = await self.db.fetch_one(query, {"key": key})
        return SystemConfig(**result) if result else None

    async def get_all_config(self) -> List[SystemConfig]:
        """Get all configuration values"""
        query = "SELECT * FROM system_configs ORDER BY key"
        results = await self.db.fetch_all(query)
        return [SystemConfig(**result) for result in results]

    async def create_config(self, config_data: SystemConfigCreate) -> SystemConfig:
        """Create new configuration"""
        query = """
        INSERT INTO system_configs (id, key, value, type, description, updated_at)
        VALUES (:id, :key, :value, :type, :description, :updated_at)
        RETURNING *
        """
        
        config_id = str(uuid.uuid4())
        values = {
            "id": config_id,
            "key": config_data.key,
            "value": config_data.value,
            "type": config_data.type,
            "description": config_data.description,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.db.fetch_one(query, values)
        return SystemConfig(**result) if result else None

    async def update_config(
        self, 
        key: str, 
        config_update: SystemConfigUpdate
    ) -> Optional[SystemConfig]:
        """Update configuration value"""
        set_clauses = ["updated_at = :updated_at"]
        values = {"key": key, "updated_at": datetime.utcnow()}
        
        if config_update.value is not None:
            set_clauses.append("value = :value")
            values["value"] = config_update.value
            
        if config_update.description is not None:
            set_clauses.append("description = :description")
            values["description"] = config_update.description
        
        query = f"""
        UPDATE system_configs 
        SET {', '.join(set_clauses)}
        WHERE key = :key
        RETURNING *
        """
        
        result = await self.db.fetch_one(query, values)
        return SystemConfig(**result) if result else None

    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "system": {}
        }
        
        # Check database connection
        try:
            await self.db.fetch_one("SELECT 1")
            health_status["services"]["database"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["database"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "unhealthy"
        
        # Check Redis connection (if available)
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status["services"]["redis"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        
        # Check AI services
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            health_status["services"]["ai"] = {
                "status": "healthy",
                "cuda_available": cuda_available,
                "gpu_count": torch.cuda.device_count() if cuda_available else 0
            }
        except Exception as e:
            health_status["services"]["ai"] = {"status": "unhealthy", "error": str(e)}
        
        # System resources
        health_status["system"] = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": {
                "upload_dir": self._get_disk_usage(settings.UPLOAD_DIR),
                "clips_dir": self._get_disk_usage(settings.CLIPS_DIR)
            }
        }
        
        return health_status

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get detailed system statistics"""
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": psutil.virtual_memory()._asdict(),
            "disk": {
                "upload_dir": self._get_disk_usage(settings.UPLOAD_DIR),
                "clips_dir": self._get_disk_usage(settings.CLIPS_DIR),
                "temp_dir": self._get_disk_usage(settings.TEMP_DIR)
            },
            "network": self._get_network_stats()
        }
        
        # Database statistics
        try:
            db_stats = await self._get_database_stats()
            stats["database"] = db_stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            stats["database"] = {"error": str(e)}
        
        # AI/GPU statistics
        try:
            gpu_stats = self._get_gpu_stats()
            stats["gpu"] = gpu_stats
        except Exception as e:
            logger.error(f"Error getting GPU stats: {e}")
            stats["gpu"] = {"error": str(e)}
        
        return stats

    async def initialize_default_config(self):
        """Initialize default system configuration"""
        default_configs = [
            {
                "key": "auto_cleanup_enabled",
                "value": str(settings.AUTO_CLEANUP_ENABLED),
                "type": ConfigType.BOOLEAN,
                "description": "Enable automatic cleanup of old files"
            },
            {
                "key": "auto_cleanup_days",
                "value": str(settings.AUTO_CLEANUP_DAYS),
                "type": ConfigType.NUMBER,
                "description": "Number of days before files are eligible for cleanup"
            },
            {
                "key": "whisper_model",
                "value": settings.WHISPER_MODEL,
                "type": ConfigType.STRING,
                "description": "Whisper model to use for transcription"
            },
            {
                "key": "enable_gpu",
                "value": str(settings.ENABLE_GPU),
                "type": ConfigType.BOOLEAN,
                "description": "Enable GPU acceleration for AI processing"
            }
        ]
        
        for config in default_configs:
            existing = await self.get_config(config["key"])
            if not existing:
                await self.create_config(SystemConfigCreate(**config))

    def _get_disk_usage(self, path: str) -> Dict[str, Any]:
        """Get disk usage for a path"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            return {
                "total": total,
                "used": used,
                "free": free,
                "percent": (used / total) * 100 if total > 0 else 0
            }
        except Exception:
            return {"error": "Unable to get disk usage"}

    def _get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except Exception:
            return {"error": "Unable to get network stats"}

    def _get_gpu_stats(self) -> Dict[str, Any]:
        """Get GPU statistics"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpus = []
                for i in range(gpu_count):
                    gpu_props = torch.cuda.get_device_properties(i)
                    memory_allocated = torch.cuda.memory_allocated(i)
                    memory_reserved = torch.cuda.memory_reserved(i)
                    
                    gpus.append({
                        "id": i,
                        "name": gpu_props.name,
                        "total_memory": gpu_props.total_memory,
                        "memory_allocated": memory_allocated,
                        "memory_reserved": memory_reserved,
                        "memory_free": gpu_props.total_memory - memory_reserved
                    })
                
                return {
                    "available": True,
                    "count": gpu_count,
                    "gpus": gpus
                }
            else:
                return {"available": False, "count": 0}
        except Exception as e:
            return {"available": False, "error": str(e)}

    async def _get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        # Table counts
        tables = ["videos", "clips", "highlights", "processing_tasks", "custom_prompts", "twitch_integrations"]
        for table in tables:
            count_query = f"SELECT COUNT(*) as count FROM {table}"
            result = await self.db.fetch_one(count_query)
            stats[f"{table}_count"] = result['count'] if result else 0
        
        # Recent activity
        recent_videos_query = """
        SELECT COUNT(*) as count FROM videos 
        WHERE uploaded_at > NOW() - INTERVAL '24 hours'
        """
        result = await self.db.fetch_one(recent_videos_query)
        stats["videos_last_24h"] = result['count'] if result else 0
        
        return stats
