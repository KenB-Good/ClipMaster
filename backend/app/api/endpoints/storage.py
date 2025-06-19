
"""
Storage management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from databases import Database

from app.core.database import get_db
from app.models.storage import StorageInfo
from app.services.storage_service import StorageService

router = APIRouter()

@router.get("/info", response_model=StorageInfo)
async def get_storage_info(db: Database = Depends(get_db)):
    """Get storage information"""
    storage_service = StorageService(db)
    return await storage_service.get_storage_info()

@router.post("/cleanup")
async def cleanup_storage(
    force: bool = False,
    db: Database = Depends(get_db)
):
    """Clean up old files"""
    storage_service = StorageService(db)
    result = await storage_service.cleanup_storage(force=force)
    return result

@router.get("/stats")
async def get_storage_stats(
    days: int = 30,
    db: Database = Depends(get_db)
):
    """Get storage statistics over time"""
    storage_service = StorageService(db)
    return await storage_service.get_storage_stats(days=days)

@router.post("/optimize")
async def optimize_storage(db: Database = Depends(get_db)):
    """Optimize storage by removing duplicate files"""
    storage_service = StorageService(db)
    result = await storage_service.optimize_storage()
    return result
