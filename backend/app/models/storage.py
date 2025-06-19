
"""
Storage and system models
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class ConfigType(str, Enum):
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"

class StorageInfo(BaseModel):
    total_space: int
    used_space: int
    available_space: int
    video_count: int
    clip_count: int
    usage_percentage: float

class SystemConfigBase(BaseModel):
    key: str
    value: str
    type: ConfigType = ConfigType.STRING
    description: Optional[str] = None

class SystemConfigCreate(SystemConfigBase):
    pass

class SystemConfigUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None

class SystemConfig(SystemConfigBase):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True

class StorageStats(BaseModel):
    id: str
    total_space: int
    used_space: int
    available_space: int
    video_count: int
    clip_count: int
    recorded_at: datetime

    class Config:
        from_attributes = True
