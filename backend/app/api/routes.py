
"""
Main API router
"""
from fastapi import APIRouter
from app.api.endpoints import videos, tasks, twitch, prompts, storage, system

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(twitch.router, prefix="/twitch", tags=["twitch"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(storage.router, prefix="/storage", tags=["storage"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
