
"""
Database configuration and connection
"""
import asyncpg
from databases import Database
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Database instance
database = Database(settings.DATABASE_URL)

async def get_database():
    """Get database connection"""
    return database

async def create_tables():
    """Create database tables if they don't exist"""
    try:
        await database.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

async def close_database():
    """Close database connection"""
    try:
        await database.disconnect()
        logger.info("Database disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}")

# Database connection for dependency injection
async def get_db():
    try:
        yield database
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
