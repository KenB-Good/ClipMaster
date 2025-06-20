"""
Twitch integration models
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TwitchIntegrationBase(BaseModel):
    username: str
    user_id: str
    is_monitoring: bool = False
    auto_capture: bool = False
    chat_monitoring: bool = True


class TwitchIntegrationCreate(TwitchIntegrationBase):
    access_token: str
    refresh_token: str


class TwitchIntegrationUpdate(BaseModel):
    is_monitoring: Optional[bool] = None
    auto_capture: Optional[bool] = None
    chat_monitoring: Optional[bool] = None
    last_stream_id: Optional[str] = None
    last_stream_title: Optional[str] = None
    last_stream_game: Optional[str] = None
    last_used_at: Optional[datetime] = None


class TwitchIntegration(TwitchIntegrationBase):
    id: str
    access_token: Optional[str] = Field(default=None, exclude=True)
    refresh_token: Optional[str] = Field(default=None, exclude=True)
    last_stream_id: Optional[str] = None
    last_stream_title: Optional[str] = None
    last_stream_game: Optional[str] = None
    connected_at: datetime
    last_used_at: datetime

    class Config:
        from_attributes = True
