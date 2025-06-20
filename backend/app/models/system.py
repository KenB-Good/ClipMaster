from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel

from .storage import SystemConfig as StorageSystemConfig, SystemConfigUpdate


class SystemConfig(StorageSystemConfig):
    """System configuration model aliasing storage model."""

    pass


class ConfigUpdate(SystemConfigUpdate):
    """Data model for updating system configuration."""

    pass


class SystemStats(BaseModel):
    """Runtime system statistics."""

    cpu_percent: float
    cpu_count: int
    memory_total: int
    memory_used: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float
    gpu_usage: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True
