import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def connect_to_mongo():
    """Create database connection"""
    try:
        # Get MongoDB URI from environment variable
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        
        # Create client
        db.client = AsyncIOMotorClient(mongo_uri)
        
        # Test connection
        await db.client.admin.command('ismaster')
        
        # Get database
        database_name = os.getenv("DATABASE_NAME", "emogo_db")
        db.database = db.client[database_name]
        
        logger.info(f"Connected to MongoDB at {mongo_uri}")
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        # Don't raise the error, just log it
        # This allows the app to start even without MongoDB
        pass


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


async def get_database():
    """Get database instance"""
    try:
        # Check if database connection exists
        if db.database is None:
            await connect_to_mongo()
        return db.database
    except Exception as e:
        logger.error(f"Error getting database: {e}")
        return None


# Collection names
VLOGS_COLLECTION = "vlogs"
SENTIMENTS_COLLECTION = "sentiments"
GPS_COLLECTION = "gps_coordinates"
