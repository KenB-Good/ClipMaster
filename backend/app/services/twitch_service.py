"""
Twitch service for integration management
"""

import base64
import hashlib
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

from app.core.config import settings
from app.models.twitch import (
    TwitchIntegration,
    TwitchIntegrationCreate,
    TwitchIntegrationUpdate,
)
from app.twitch.client import TwitchAPIClient
from cryptography.fernet import Fernet
from databases import Database

logger = logging.getLogger(__name__)


class TwitchService:
    def __init__(self, db: Database):
        self.db = db
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(key))
        self.twitch_client = TwitchAPIClient()

    def _encrypt(self, token: str) -> str:
        return self._fernet.encrypt(token.encode()).decode()

    def _decrypt(self, token: str) -> str:
        return self._fernet.decrypt(token.encode()).decode()

    def _decrypt_row(self, row: Mapping[str, Any]) -> Dict[str, Any]:
        data = dict(row)
        if "access_token" in data and data["access_token"]:
            data["access_token"] = self._decrypt(data["access_token"])
        if "refresh_token" in data and data["refresh_token"]:
            data["refresh_token"] = self._decrypt(data["refresh_token"])
        return data

    async def create_integration(
        self, integration_data: TwitchIntegrationCreate
    ) -> TwitchIntegration:
        """Create a new Twitch integration"""
        query = """
        INSERT INTO twitch_integrations (id, access_token, refresh_token, username, user_id,
                                       is_monitoring, auto_capture, chat_monitoring, 
                                       connected_at, last_used_at)
        VALUES (:id, :access_token, :refresh_token, :username, :user_id,
                :is_monitoring, :auto_capture, :chat_monitoring, :connected_at, :last_used_at)
        RETURNING *
        """

        integration_id = str(uuid.uuid4())
        now = datetime.utcnow()

        values = {
            "id": integration_id,
            "access_token": self._encrypt(integration_data.access_token),
            "refresh_token": self._encrypt(integration_data.refresh_token),
            "username": integration_data.username,
            "user_id": integration_data.user_id,
            "is_monitoring": integration_data.is_monitoring,
            "auto_capture": integration_data.auto_capture,
            "chat_monitoring": integration_data.chat_monitoring,
            "connected_at": now,
            "last_used_at": now,
        }

        result = await self.db.fetch_one(query, values)
        return TwitchIntegration(**self._decrypt_row(result)) if result else None

    async def get_integration(self, integration_id: str) -> Optional[TwitchIntegration]:
        """Get integration by ID"""
        query = "SELECT * FROM twitch_integrations WHERE id = :integration_id"
        result = await self.db.fetch_one(query, {"integration_id": integration_id})
        return TwitchIntegration(**self._decrypt_row(result)) if result else None

    async def get_integrations(self) -> List[TwitchIntegration]:
        """Get all integrations"""
        query = "SELECT * FROM twitch_integrations ORDER BY connected_at DESC"
        results = await self.db.fetch_all(query)
        return [TwitchIntegration(**self._decrypt_row(result)) for result in results]

    async def update_integration(
        self, integration_id: str, integration_update: TwitchIntegrationUpdate
    ) -> Optional[TwitchIntegration]:
        """Update integration"""
        set_clauses = []
        values = {"integration_id": integration_id}

        if integration_update.is_monitoring is not None:
            set_clauses.append("is_monitoring = :is_monitoring")
            values["is_monitoring"] = integration_update.is_monitoring

        if integration_update.auto_capture is not None:
            set_clauses.append("auto_capture = :auto_capture")
            values["auto_capture"] = integration_update.auto_capture

        if integration_update.chat_monitoring is not None:
            set_clauses.append("chat_monitoring = :chat_monitoring")
            values["chat_monitoring"] = integration_update.chat_monitoring

        if integration_update.last_stream_id is not None:
            set_clauses.append("last_stream_id = :last_stream_id")
            values["last_stream_id"] = integration_update.last_stream_id

        if integration_update.last_stream_title is not None:
            set_clauses.append("last_stream_title = :last_stream_title")
            values["last_stream_title"] = integration_update.last_stream_title

        if integration_update.last_stream_game is not None:
            set_clauses.append("last_stream_game = :last_stream_game")
            values["last_stream_game"] = integration_update.last_stream_game

        if integration_update.last_used_at is not None:
            set_clauses.append("last_used_at = :last_used_at")
            values["last_used_at"] = integration_update.last_used_at

        if not set_clauses:
            return await self.get_integration(integration_id)

        query = f"""
        UPDATE twitch_integrations 
        SET {', '.join(set_clauses)}
        WHERE id = :integration_id
        RETURNING *
        """

        result = await self.db.fetch_one(query, values)
        return TwitchIntegration(**self._decrypt_row(result)) if result else None

    async def delete_integration(self, integration_id: str) -> bool:
        """Delete integration"""
        query = "DELETE FROM twitch_integrations WHERE id = :integration_id"
        result = await self.db.execute(query, {"integration_id": integration_id})
        return result > 0

    async def get_stream_info(self, user_id: str) -> Dict[str, Any]:
        """Get current stream information"""
        try:
            return await self.twitch_client.get_stream_info(user_id)
        except Exception as exc:
            logger.error(f"Failed to fetch stream info: {exc}")
            return {"is_live": False, "error": str(exc)}

    async def handle_auth_callback(
        self, code: str, state: Optional[str] = None
    ) -> TwitchIntegration:
        """Handle Twitch OAuth callback"""
        token_data = await self.twitch_client.exchange_code_for_token(code)
        user_info = await self.twitch_client.get_user_info(token_data["access_token"])
        integration_data = TwitchIntegrationCreate(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            username=user_info["login"],
            user_id=user_info["id"],
        )
        return await self.create_integration(integration_data)

    async def refresh_token(self, integration_id: str) -> bool:
        """Refresh access token"""
        query = "SELECT refresh_token FROM twitch_integrations WHERE id = :id"
        row = await self.db.fetch_one(query, {"id": integration_id})
        if not row:
            return False
        refresh_token = self._decrypt(row["refresh_token"])
        tokens = await self.twitch_client.refresh_access_token(refresh_token)
        update_query = (
            "UPDATE twitch_integrations SET access_token=:access, refresh_token=:refresh, last_used_at=:used"
            " WHERE id=:id"
        )
        await self.db.execute(
            update_query,
            {
                "access": self._encrypt(tokens["access_token"]),
                "refresh": self._encrypt(tokens["refresh_token"]),
                "used": datetime.utcnow(),
                "id": integration_id,
            },
        )
        return True

    async def get_user_by_username(self, username: str) -> Optional[TwitchIntegration]:
        """Get integration by username"""
        query = "SELECT * FROM twitch_integrations WHERE username = :username"
        result = await self.db.fetch_one(query, {"username": username})
        return TwitchIntegration(**self._decrypt_row(result)) if result else None
