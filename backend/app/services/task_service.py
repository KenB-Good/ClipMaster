
"""
Task service for processing task management
"""
import uuid
from typing import List, Optional
from datetime import datetime
from databases import Database

from app.models.task import ProcessingTask, ProcessingTaskCreate, ProcessingTaskUpdate, TaskStatus, TaskType
import logging

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db: Database):
        self.db = db

    async def create_task(self, task_data: ProcessingTaskCreate) -> ProcessingTask:
        """Create a new processing task"""
        query = """
        INSERT INTO processing_tasks (id, video_id, type, status, progress, config, custom_prompt, created_at)
        VALUES (:id, :video_id, :type, :status, :progress, :config, :custom_prompt, :created_at)
        RETURNING *
        """
        
        task_id = str(uuid.uuid4())
        values = {
            "id": task_id,
            "video_id": task_data.video_id,
            "type": task_data.type,
            "status": TaskStatus.PENDING,
            "progress": 0.0,
            "config": task_data.config,
            "custom_prompt": task_data.custom_prompt,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.fetch_one(query, values)
        return ProcessingTask(**result) if result else None

    async def get_task(self, task_id: str) -> Optional[ProcessingTask]:
        """Get task by ID"""
        query = "SELECT * FROM processing_tasks WHERE id = :task_id"
        result = await self.db.fetch_one(query, {"task_id": task_id})
        return ProcessingTask(**result) if result else None

    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        video_id: Optional[str] = None
    ) -> List[ProcessingTask]:
        """Get list of tasks with filters"""
        where_clauses = []
        values = {"skip": skip, "limit": limit}
        
        if status:
            where_clauses.append("status = :status")
            values["status"] = status
            
        if task_type:
            where_clauses.append("type = :task_type")
            values["task_type"] = task_type
            
        if video_id:
            where_clauses.append("video_id = :video_id")
            values["video_id"] = video_id
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT * FROM processing_tasks 
        {where_clause}
        ORDER BY created_at DESC 
        OFFSET :skip LIMIT :limit
        """
        
        results = await self.db.fetch_all(query, values)
        return [ProcessingTask(**result) for result in results]

    async def update_task(self, task_id: str, task_update: ProcessingTaskUpdate) -> Optional[ProcessingTask]:
        """Update task"""
        set_clauses = []
        values = {"task_id": task_id}
        
        if task_update.status is not None:
            set_clauses.append("status = :status")
            values["status"] = task_update.status
            
        if task_update.progress is not None:
            set_clauses.append("progress = :progress")
            values["progress"] = task_update.progress
            
        if task_update.result is not None:
            set_clauses.append("result = :result")
            values["result"] = task_update.result
            
        if task_update.error is not None:
            set_clauses.append("error = :error")
            values["error"] = task_update.error
            
        if task_update.started_at is not None:
            set_clauses.append("started_at = :started_at")
            values["started_at"] = task_update.started_at
            
        if task_update.completed_at is not None:
            set_clauses.append("completed_at = :completed_at")
            values["completed_at"] = task_update.completed_at
        
        if not set_clauses:
            return await self.get_task(task_id)
        
        query = f"""
        UPDATE processing_tasks 
        SET {', '.join(set_clauses)}
        WHERE id = :task_id
        RETURNING *
        """
        
        result = await self.db.fetch_one(query, values)
        return ProcessingTask(**result) if result else None

    async def cancel_task(self, task_id: str) -> Optional[ProcessingTask]:
        """Cancel a task"""
        update_data = ProcessingTaskUpdate(
            status=TaskStatus.CANCELLED,
            completed_at=datetime.utcnow()
        )
        return await self.update_task(task_id, update_data)

    async def retry_task(self, task_id: str) -> Optional[ProcessingTask]:
        """Retry a failed task"""
        update_data = ProcessingTaskUpdate(
            status=TaskStatus.PENDING,
            progress=0.0,
            error=None,
            started_at=None,
            completed_at=None
        )
        return await self.update_task(task_id, update_data)

    async def get_video_tasks(self, video_id: str) -> List[ProcessingTask]:
        """Get all tasks for a video"""
        query = """
        SELECT * FROM processing_tasks 
        WHERE video_id = :video_id 
        ORDER BY created_at DESC
        """
        results = await self.db.fetch_all(query, {"video_id": video_id})
        return [ProcessingTask(**result) for result in results]

    async def get_pending_tasks(self, task_type: Optional[TaskType] = None) -> List[ProcessingTask]:
        """Get pending tasks for processing"""
        where_clause = "WHERE status = :status"
        values = {"status": TaskStatus.PENDING}
        
        if task_type:
            where_clause += " AND type = :task_type"
            values["task_type"] = task_type
        
        query = f"""
        SELECT * FROM processing_tasks 
        {where_clause}
        ORDER BY created_at ASC
        """
        
        results = await self.db.fetch_all(query, values)
        return [ProcessingTask(**result) for result in results]
