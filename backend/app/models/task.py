
"""
Processing task models
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    TRANSCRIPTION = "TRANSCRIPTION"
    HIGHLIGHT_DETECTION = "HIGHLIGHT_DETECTION"
    CLIP_GENERATION = "CLIP_GENERATION"
    SUBTITLE_GENERATION = "SUBTITLE_GENERATION"
    TWITCH_CAPTURE = "TWITCH_CAPTURE"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ProcessingTaskBase(BaseModel):
    type: TaskType
    config: Optional[Dict[str, Any]] = None
    custom_prompt: Optional[str] = None

class ProcessingTaskCreate(ProcessingTaskBase):
    video_id: Optional[str] = None

class ProcessingTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ProcessingTask(ProcessingTaskBase):
    id: str
    video_id: Optional[str] = None
    status: TaskStatus
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
