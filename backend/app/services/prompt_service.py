"""
Custom prompt service for ClipMaster
Handles user-defined prompts for highlight detection
SECURITY: Fixed SQL injection vulnerabilities with parameterized queries
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import text
from ..core.database import database
from ..models.prompt import CustomPrompt, PromptCreate, PromptUpdate

logger = logging.getLogger(__name__)


class PromptService:
    """Service for managing custom prompts"""

    async def create_prompt(
        self, prompt_data: PromptCreate, user_id: int
    ) -> CustomPrompt:
        """Create a new custom prompt"""
        try:
            # SECURITY FIX: Use parameterized query instead of f-string
            query = text(
                """
                INSERT INTO custom_prompts (user_id, name, description, keywords, category, is_active)
                VALUES (:user_id, :name, :description, :keywords, :category, :is_active)
                RETURNING *
            """
            )

            values = {
                "user_id": user_id,
                "name": prompt_data.name,
                "description": prompt_data.description,
                "keywords": prompt_data.keywords,
                "category": prompt_data.category,
                "is_active": prompt_data.is_active,
            }

            result = await database.fetch_one(query, values)
            return CustomPrompt(**result) if result else None

        except Exception as e:
            logger.error(f"Error creating prompt: {e}")
            raise

    async def get_prompts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
    ) -> List[CustomPrompt]:
        """Get user's custom prompts with optional filtering"""
        try:
            # SECURITY FIX: Use parameterized query with proper WHERE clause construction
            base_query = """
                SELECT * FROM custom_prompts 
                WHERE user_id = :user_id
            """

            values = {"user_id": user_id, "skip": skip, "limit": limit}

            # Safely add category filter if provided
            if category:
                base_query += " AND category = :category"
                values["category"] = category

            # Complete the query with ordering and pagination
            query = text(
                base_query
                + """
                ORDER BY use_count DESC, created_at DESC 
                OFFSET :skip LIMIT :limit
            """
            )

            results = await database.fetch_all(query, values)
            return [CustomPrompt(**result) for result in results]

        except Exception as e:
            logger.error(f"Error fetching prompts: {e}")
            raise

    async def get_prompt(self, prompt_id: int, user_id: int) -> Optional[CustomPrompt]:
        """Get a specific prompt by ID"""
        try:
            # SECURITY FIX: Use parameterized query
            query = text(
                """
                SELECT * FROM custom_prompts 
                WHERE id = :prompt_id AND user_id = :user_id
            """
            )

            values = {"prompt_id": prompt_id, "user_id": user_id}

            result = await database.fetch_one(query, values)
            return CustomPrompt(**result) if result else None

        except Exception as e:
            logger.error(f"Error fetching prompt {prompt_id}: {e}")
            raise

    async def update_prompt(
        self, prompt_id: int, prompt_update: PromptUpdate, user_id: int
    ) -> Optional[CustomPrompt]:
        """Update an existing prompt"""
        try:
            # Build update query dynamically but safely
            set_clauses = []
            values = {
                "prompt_id": prompt_id,
                "user_id": user_id,
                "updated_at": datetime.utcnow(),
            }

            # SECURITY FIX: Build SET clauses safely without f-strings
            if prompt_update.name is not None:
                set_clauses.append("name = :name")
                values["name"] = prompt_update.name

            if prompt_update.description is not None:
                set_clauses.append("description = :description")
                values["description"] = prompt_update.description

            if prompt_update.keywords is not None:
                set_clauses.append("keywords = :keywords")
                values["keywords"] = prompt_update.keywords

            if prompt_update.category is not None:
                set_clauses.append("category = :category")
                values["category"] = prompt_update.category

            if prompt_update.is_active is not None:
                set_clauses.append("is_active = :is_active")
                values["is_active"] = prompt_update.is_active

            if not set_clauses:
                # No updates to make
                return await self.get_prompt(prompt_id, user_id)

            # Add updated_at to SET clauses
            set_clauses.append("updated_at = :updated_at")

            # SECURITY FIX: Use parameterized query with safe SET clause construction
            query = text(
                f"""
                UPDATE custom_prompts 
                SET {', '.join(set_clauses)}
                WHERE id = :prompt_id AND user_id = :user_id
                RETURNING *
            """
            )

            result = await database.fetch_one(query, values)
            return CustomPrompt(**result) if result else None

        except Exception as e:
            logger.error(f"Error updating prompt {prompt_id}: {e}")
            raise

    async def delete_prompt(self, prompt_id: int, user_id: int) -> bool:
        """Delete a prompt"""
        try:
            # SECURITY FIX: Use parameterized query
            query = text(
                """
                DELETE FROM custom_prompts 
                WHERE id = :prompt_id AND user_id = :user_id
            """
            )

            values = {"prompt_id": prompt_id, "user_id": user_id}

            result = await database.execute(query, values)
            return result > 0

        except Exception as e:
            logger.error(f"Error deleting prompt {prompt_id}: {e}")
            raise

    async def increment_use_count(self, prompt_id: int, user_id: int) -> bool:
        """Increment the use count for a prompt"""
        try:
            # SECURITY FIX: Use parameterized query
            query = text(
                """
                UPDATE custom_prompts 
                SET use_count = use_count + 1, last_used = :last_used
                WHERE id = :prompt_id AND user_id = :user_id
            """
            )

            values = {
                "prompt_id": prompt_id,
                "user_id": user_id,
                "last_used": datetime.utcnow(),
            }

            result = await database.execute(query, values)
            return result > 0

        except Exception as e:
            logger.error(f"Error incrementing use count for prompt {prompt_id}: {e}")
            raise

    async def get_popular_prompts(self, limit: int = 10) -> List[CustomPrompt]:
        """Get most popular prompts across all users"""
        try:
            # SECURITY FIX: Use parameterized query
            query = text(
                """
                SELECT * FROM custom_prompts 
                WHERE is_active = true
                ORDER BY use_count DESC, created_at DESC 
                LIMIT :limit
            """
            )

            values = {"limit": limit}

            results = await database.fetch_all(query, values)
            return [CustomPrompt(**result) for result in results]

        except Exception as e:
            logger.error(f"Error fetching popular prompts: {e}")
            raise

    async def search_prompts(
        self, user_id: int, search_term: str, limit: int = 50
    ) -> List[CustomPrompt]:
        """Search prompts by name, description, or keywords"""
        try:
            # SECURITY FIX: Use parameterized query with ILIKE for case-insensitive search
            query = text(
                """
                SELECT * FROM custom_prompts 
                WHERE user_id = :user_id 
                AND (
                    name ILIKE :search_pattern 
                    OR description ILIKE :search_pattern 
                    OR keywords ILIKE :search_pattern
                )
                ORDER BY use_count DESC, created_at DESC 
                LIMIT :limit
            """
            )

            search_pattern = f"%{search_term}%"
            values = {
                "user_id": user_id,
                "search_pattern": search_pattern,
                "limit": limit,
            }

            results = await database.fetch_all(query, values)
            return [CustomPrompt(**result) for result in results]

        except Exception as e:
            logger.error(f"Error searching prompts: {e}")
            raise
