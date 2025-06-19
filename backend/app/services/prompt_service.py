
"""
Custom prompt service
"""
import uuid
from typing import List, Optional
from datetime import datetime
from databases import Database

from app.models.prompt import CustomPrompt, CustomPromptCreate, CustomPromptUpdate, PromptCategory
import logging

logger = logging.getLogger(__name__)

class PromptService:
    def __init__(self, db: Database):
        self.db = db

    async def create_prompt(self, prompt_data: CustomPromptCreate) -> CustomPrompt:
        """Create a new custom prompt"""
        query = """
        INSERT INTO custom_prompts (id, name, description, prompt, category, use_count, created_at, updated_at)
        VALUES (:id, :name, :description, :prompt, :category, :use_count, :created_at, :updated_at)
        RETURNING *
        """
        
        prompt_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        values = {
            "id": prompt_id,
            "name": prompt_data.name,
            "description": prompt_data.description,
            "prompt": prompt_data.prompt,
            "category": prompt_data.category,
            "use_count": 0,
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.db.fetch_one(query, values)
        return CustomPrompt(**result) if result else None

    async def get_prompt(self, prompt_id: str) -> Optional[CustomPrompt]:
        """Get prompt by ID"""
        query = "SELECT * FROM custom_prompts WHERE id = :prompt_id"
        result = await self.db.fetch_one(query, {"prompt_id": prompt_id})
        return CustomPrompt(**result) if result else None

    async def get_prompts(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[PromptCategory] = None
    ) -> List[CustomPrompt]:
        """Get list of prompts"""
        where_clause = ""
        values = {"skip": skip, "limit": limit}
        
        if category:
            where_clause = "WHERE category = :category"
            values["category"] = category
        
        query = f"""
        SELECT * FROM custom_prompts 
        {where_clause}
        ORDER BY use_count DESC, created_at DESC 
        OFFSET :skip LIMIT :limit
        """
        
        results = await self.db.fetch_all(query, values)
        return [CustomPrompt(**result) for result in results]

    async def update_prompt(
        self, 
        prompt_id: str, 
        prompt_update: CustomPromptUpdate
    ) -> Optional[CustomPrompt]:
        """Update prompt"""
        set_clauses = ["updated_at = :updated_at"]
        values = {"prompt_id": prompt_id, "updated_at": datetime.utcnow()}
        
        if prompt_update.name is not None:
            set_clauses.append("name = :name")
            values["name"] = prompt_update.name
            
        if prompt_update.description is not None:
            set_clauses.append("description = :description")
            values["description"] = prompt_update.description
            
        if prompt_update.prompt is not None:
            set_clauses.append("prompt = :prompt")
            values["prompt"] = prompt_update.prompt
            
        if prompt_update.category is not None:
            set_clauses.append("category = :category")
            values["category"] = prompt_update.category
        
        query = f"""
        UPDATE custom_prompts 
        SET {', '.join(set_clauses)}
        WHERE id = :prompt_id
        RETURNING *
        """
        
        result = await self.db.fetch_one(query, values)
        return CustomPrompt(**result) if result else None

    async def delete_prompt(self, prompt_id: str) -> bool:
        """Delete prompt"""
        query = "DELETE FROM custom_prompts WHERE id = :prompt_id"
        result = await self.db.execute(query, {"prompt_id": prompt_id})
        return result > 0

    async def use_prompt(self, prompt_id: str) -> Optional[CustomPrompt]:
        """Increment use count for a prompt"""
        query = """
        UPDATE custom_prompts 
        SET use_count = use_count + 1, last_used_at = :last_used_at
        WHERE id = :prompt_id
        RETURNING *
        """
        
        values = {
            "prompt_id": prompt_id,
            "last_used_at": datetime.utcnow()
        }
        
        result = await self.db.fetch_one(query, values)
        return CustomPrompt(**result) if result else None

    async def get_popular_prompts(self, limit: int = 10) -> List[CustomPrompt]:
        """Get most popular prompts"""
        query = """
        SELECT * FROM custom_prompts 
        WHERE use_count > 0
        ORDER BY use_count DESC 
        LIMIT :limit
        """
        
        results = await self.db.fetch_all(query, {"limit": limit})
        return [CustomPrompt(**result) for result in results]

    async def search_prompts(self, search_term: str, limit: int = 50) -> List[CustomPrompt]:
        """Search prompts by name or content"""
        query = """
        SELECT * FROM custom_prompts 
        WHERE name ILIKE :search_term OR prompt ILIKE :search_term
        ORDER BY use_count DESC 
        LIMIT :limit
        """
        
        search_pattern = f"%{search_term}%"
        results = await self.db.fetch_all(query, {"search_term": search_pattern, "limit": limit})
        return [CustomPrompt(**result) for result in results]
