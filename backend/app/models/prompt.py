
"""
Custom prompt models
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class PromptCategory(str, Enum):
    GENERAL = "GENERAL"
    GAMING = "GAMING"
    REACTIONS = "REACTIONS"
    EDUCATIONAL = "EDUCATIONAL"
    ENTERTAINMENT = "ENTERTAINMENT"

class CustomPromptBase(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    category: PromptCategory = PromptCategory.GENERAL

class CustomPromptCreate(CustomPromptBase):
    pass

class CustomPromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    category: Optional[PromptCategory] = None

class CustomPrompt(CustomPromptBase):
    id: str
    use_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
