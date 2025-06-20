
"""
Custom prompt management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from databases import Database

from app.core.database import get_db
from app.models.prompt import CustomPrompt, CustomPromptCreate, CustomPromptUpdate, PromptCategory
from app.services.prompt_service import PromptService

router = APIRouter()

@router.get("/", response_model=List[CustomPrompt])
async def get_prompts(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    category: Optional[PromptCategory] = None,
    db: Database = Depends(get_db)
):
    """Get custom prompts"""
    prompt_service = PromptService()
    return await prompt_service.get_prompts(
        user_id=user_id, skip=skip, limit=limit, category=category
    )

@router.get("/{prompt_id}", response_model=CustomPrompt)
async def get_prompt(prompt_id: str, user_id: int, db: Database = Depends(get_db)):
    """Get prompt by ID"""
    prompt_service = PromptService()
    prompt = await prompt_service.get_prompt(prompt_id, user_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.post("/", response_model=CustomPrompt)
async def create_prompt(
    prompt_data: CustomPromptCreate,
    user_id: int,
    db: Database = Depends(get_db)
):
    """Create a new custom prompt"""
    prompt_service = PromptService()
    return await prompt_service.create_prompt(prompt_data, user_id)

@router.put("/{prompt_id}", response_model=CustomPrompt)
async def update_prompt(
    prompt_id: str,
    prompt_update: CustomPromptUpdate,
    user_id: int,
    db: Database = Depends(get_db)
):
    """Update custom prompt"""
    prompt_service = PromptService()
    prompt = await prompt_service.update_prompt(prompt_id, prompt_update, user_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str, user_id: int, db: Database = Depends(get_db)):
    """Delete custom prompt"""
    prompt_service = PromptService()
    await prompt_service.delete_prompt(prompt_id, user_id)
    return {"message": "Prompt deleted successfully"}

@router.post("/{prompt_id}/use")
async def use_prompt(prompt_id: str, user_id: int, db: Database = Depends(get_db)):
    """Increment the usage count for a prompt"""
    prompt_service = PromptService()
    success = await prompt_service.increment_use_count(prompt_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"message": "Prompt usage recorded"}

@router.get("/categories/", response_model=List[str])
async def get_categories():
    """Get available prompt categories"""
    return [category.value for category in PromptCategory]
