
"""
Task management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from databases import Database

from app.core.database import get_db
from app.models.task import ProcessingTask, ProcessingTaskCreate, ProcessingTaskUpdate, TaskStatus, TaskType
from app.services.task_service import TaskService

router = APIRouter()

@router.get("/", response_model=List[ProcessingTask])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    video_id: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Get processing tasks"""
    task_service = TaskService(db)
    return await task_service.get_tasks(
        skip=skip, 
        limit=limit, 
        status=status, 
        task_type=task_type,
        video_id=video_id
    )

@router.get("/{task_id}", response_model=ProcessingTask)
async def get_task(task_id: str, db: Database = Depends(get_db)):
    """Get task by ID"""
    task_service = TaskService(db)
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=ProcessingTask)
async def create_task(
    task_data: ProcessingTaskCreate,
    db: Database = Depends(get_db)
):
    """Create a new processing task"""
    task_service = TaskService(db)
    return await task_service.create_task(task_data)

@router.put("/{task_id}", response_model=ProcessingTask)
async def update_task(
    task_id: str,
    task_update: ProcessingTaskUpdate,
    db: Database = Depends(get_db)
):
    """Update task status"""
    task_service = TaskService(db)
    task = await task_service.update_task(task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}")
async def cancel_task(task_id: str, db: Database = Depends(get_db)):
    """Cancel a task"""
    task_service = TaskService(db)
    task = await task_service.cancel_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task cancelled successfully"}

@router.get("/video/{video_id}", response_model=List[ProcessingTask])
async def get_video_tasks(video_id: str, db: Database = Depends(get_db)):
    """Get all tasks for a video"""
    task_service = TaskService(db)
    return await task_service.get_video_tasks(video_id)

@router.post("/retry/{task_id}")
async def retry_task(task_id: str, db: Database = Depends(get_db)):
    """Retry a failed task"""
    task_service = TaskService(db)
    task = await task_service.retry_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task queued for retry", "task_id": task_id}
