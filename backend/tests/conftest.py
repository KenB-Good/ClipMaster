import os
import tempfile
import pytest
import pytest_asyncio
from databases import Database

@pytest.fixture(autouse=True, scope="session")
def set_env():
    os.environ.setdefault("SECRET_KEY", "testsecret")

@pytest_asyncio.fixture
async def db(tmp_path):
    db_path = tmp_path / "test.db"
    database = Database(f"sqlite+aiosqlite:///{db_path}")
    await database.connect()
    # videos table
    await database.execute(
        """
        CREATE TABLE videos(
            id TEXT PRIMARY KEY,
            filename TEXT,
            original_filename TEXT,
            file_path TEXT,
            file_size INTEGER,
            format TEXT,
            resolution TEXT,
            source TEXT,
            twitch_stream_id TEXT,
            twitch_title TEXT,
            twitch_game TEXT,
            uploaded_at TEXT,
            processed_at TEXT,
            status TEXT,
            transcription TEXT
        )
        """
    )
    await database.execute(
        """
        CREATE TABLE highlights(
            id TEXT PRIMARY KEY,
            video_id TEXT,
            start_time REAL,
            end_time REAL,
            confidence REAL,
            type TEXT,
            description TEXT,
            created_at TEXT
        )
        """
    )
    await database.execute(
        """
        CREATE TABLE clips(
            id TEXT PRIMARY KEY,
            video_id TEXT,
            highlight_id TEXT,
            filename TEXT,
            file_path TEXT,
            file_size INTEGER,
            duration REAL,
            start_time REAL,
            end_time REAL,
            format TEXT,
            created_at TEXT
        )
        """
    )
    await database.execute(
        """
        CREATE TABLE twitch_integrations(
            id TEXT PRIMARY KEY,
            access_token TEXT,
            refresh_token TEXT,
            username TEXT,
            user_id TEXT,
            is_monitoring BOOLEAN,
            auto_capture BOOLEAN,
            chat_monitoring BOOLEAN,
            last_stream_id TEXT,
            last_stream_title TEXT,
            last_stream_game TEXT,
            connected_at TEXT,
            last_used_at TEXT
        )
        """
    )
    yield database
    await database.disconnect()

