
"""
System configuration endpoints
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from databases import Database

from app.core.database import get_db
from app.models.storage import SystemConfig, SystemConfigCreate, SystemConfigUpdate
from app.services.system_service import SystemService

router = APIRouter()

@router.get("/config", response_model=List[SystemConfig])
async def get_system_config(db: Database = Depends(get_db)):
    """Get system configuration"""
    system_service = SystemService(db)
    return await system_service.get_all_config()

@router.get("/config/{key}", response_model=SystemConfig)
async def get_config_value(key: str, db: Database = Depends(get_db)):
    """Get specific configuration value"""
    system_service = SystemService(db)
    config = await system_service.get_config(key)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.post("/config", response_model=SystemConfig)
async def create_config(
    config_data: SystemConfigCreate,
    db: Database = Depends(get_db)
):
    """Create system configuration"""
    system_service = SystemService(db)
    return await system_service.create_config(config_data)

@router.put("/config/{key}", response_model=SystemConfig)
async def update_config(
    key: str,
    config_update: SystemConfigUpdate,
    db: Database = Depends(get_db)
):
    """Update system configuration"""
    system_service = SystemService(db)
    config = await system_service.update_config(key, config_update)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.get("/health")
async def system_health(db: Database = Depends(get_db)):
    """Get system health status"""
    system_service = SystemService(db)
    return await system_service.get_health_status()

@router.get("/stats")
async def system_stats(db: Database = Depends(get_db)):
    """Get system statistics"""
    system_service = SystemService(db)
    return await system_service.get_system_stats()

@router.post("/test-ai")
async def test_ai_services():
    """Test AI service availability"""
    try:
        from app.services.ai_service import AIService
        ai_service = AIService()
        result = await ai_service.test_services()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service test failed: {str(e)}")
