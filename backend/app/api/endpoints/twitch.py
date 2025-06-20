"""
Twitch integration endpoints
"""

from typing import List, Optional

from app.core.database import get_db
from app.models.twitch import (
    TwitchIntegration,
    TwitchIntegrationCreate,
    TwitchIntegrationUpdate,
)
from app.services.twitch_service import TwitchService
from databases import Database
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

router = APIRouter()


@router.get("/", response_model=List[TwitchIntegration])
async def get_integrations(db: Database = Depends(get_db)):
    """Get Twitch integrations"""
    twitch_service = TwitchService(db)
    return await twitch_service.get_integrations()


@router.get("/{integration_id}", response_model=TwitchIntegration)
async def get_integration(integration_id: str, db: Database = Depends(get_db)):
    """Get Twitch integration by ID"""
    twitch_service = TwitchService(db)
    integration = await twitch_service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.post("/", response_model=TwitchIntegration)
async def create_integration(
    integration_data: TwitchIntegrationCreate, db: Database = Depends(get_db)
):
    """Create Twitch integration"""
    twitch_service = TwitchService(db)
    return await twitch_service.create_integration(integration_data)


@router.put("/{integration_id}", response_model=TwitchIntegration)
async def update_integration(
    integration_id: str,
    integration_update: TwitchIntegrationUpdate,
    db: Database = Depends(get_db),
):
    """Update Twitch integration"""
    twitch_service = TwitchService(db)
    integration = await twitch_service.update_integration(
        integration_id, integration_update
    )
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.delete("/{integration_id}")
async def delete_integration(integration_id: str, db: Database = Depends(get_db)):
    """Delete Twitch integration"""
    twitch_service = TwitchService(db)
    await twitch_service.delete_integration(integration_id)
    return {"message": "Integration deleted successfully"}


@router.post("/{integration_id}/start-monitoring")
async def start_monitoring(
    integration_id: str,
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_db),
):
    """Start monitoring Twitch stream"""
    twitch_service = TwitchService(db)
    integration = await twitch_service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    # Start background monitoring
    background_tasks.add_task(monitor_stream_async, integration_id, db)

    # Update integration status
    await twitch_service.update_integration(
        integration_id, TwitchIntegrationUpdate(is_monitoring=True)
    )

    return {"message": "Stream monitoring started"}


@router.post("/{integration_id}/stop-monitoring")
async def stop_monitoring(integration_id: str, db: Database = Depends(get_db)):
    """Stop monitoring Twitch stream"""
    twitch_service = TwitchService(db)
    await twitch_service.update_integration(
        integration_id, TwitchIntegrationUpdate(is_monitoring=False)
    )
    return {"message": "Stream monitoring stopped"}


@router.get("/{integration_id}/status")
async def get_stream_status(integration_id: str, db: Database = Depends(get_db)):
    """Get current stream status"""
    twitch_service = TwitchService(db)
    integration = await twitch_service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    # Get live stream info
    stream_info = await twitch_service.get_stream_info(integration.user_id)
    return stream_info


@router.post("/auth/callback", response_model=TwitchIntegration)
async def twitch_auth_callback(
    code: str, state: Optional[str] = None, db: Database = Depends(get_db)
):
    """Handle Twitch OAuth callback"""
    twitch_service = TwitchService(db)
    integration = await twitch_service.handle_auth_callback(code, state)
    return integration


async def monitor_stream_async(integration_id: str, db: Database):
    """Background task for stream monitoring"""
    try:
        from app.services.stream_monitor import StreamMonitor

        monitor = StreamMonitor(db)
        await monitor.start_monitoring(integration_id)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Stream monitoring error: {e}")
