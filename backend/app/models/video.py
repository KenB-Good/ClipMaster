
"""
Video model for database operations
"""
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class VideoStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"
    ARCHIVED = "ARCHIVED"

class VideoSource(str, Enum):
    UPLOAD = "UPLOAD"
    TWITCH_STREAM = "TWITCH_STREAM"
    TWITCH_VOD = "TWITCH_VOD"

class ClipFormat(str, Enum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"
    SQUARE = "SQUARE"

class HighlightType(str, Enum):
    GAMEPLAY_MOMENT = "GAMEPLAY_MOMENT"
    EMOTIONAL_REACTION = "EMOTIONAL_REACTION"
    CHAT_SPIKE = "CHAT_SPIKE"
    GAMEPLAY_MECHANIC = "GAMEPLAY_MECHANIC"
    STRATEGIC_EXPLANATION = "STRATEGIC_EXPLANATION"
    CONTENT_PEAK = "CONTENT_PEAK"
    CLIP_THAT_MOMENT = "CLIP_THAT_MOMENT"
    CUSTOM_PROMPT = "CUSTOM_PROMPT"

class VideoBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    duration: Optional[float] = None
    format: str
    resolution: Optional[str] = None
    source: VideoSource = VideoSource.UPLOAD
    twitch_stream_id: Optional[str] = None
    twitch_title: Optional[str] = None
    twitch_game: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    status: Optional[VideoStatus] = None
    transcription: Optional[str] = None
    processed_at: Optional[datetime] = None

class Video(VideoBase):
    id: str
    file_path: str
    status: VideoStatus
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    transcription: Optional[str] = None

    class Config:
        from_attributes = True

class HighlightBase(BaseModel):
    start_time: float
    end_time: float
    confidence: float
    type: HighlightType
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class HighlightCreate(HighlightBase):
    video_id: str

class Highlight(HighlightBase):
    id: str
    video_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ClipBase(BaseModel):
    filename: str
    file_size: int
    duration: float
    start_time: float
    end_time: float
    format: ClipFormat = ClipFormat.HORIZONTAL
    has_subtitles: bool = False
    has_overlay: bool = False
    overlay_config: Optional[Dict[str, Any]] = None

class ClipCreate(ClipBase):
    video_id: str
    highlight_id: Optional[str] = None
    file_path: str

class Clip(ClipBase):
    id: str
    video_id: str
    highlight_id: Optional[str] = None
    file_path: str
    created_at: datetime
    downloaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
