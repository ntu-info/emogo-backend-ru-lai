import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

# Import memory database as fallback
from memory_db import get_memory_collection

class Database:
    client: AsyncIOMotorClient = None
    database = None
    use_memory = False


db = Database()


async def connect_to_mongo():
    """Create database connection"""
    try:
        # Get MongoDB URI from environment variable
        mongo_uri = os.getenv("MONGODB_URI")
        
        if not mongo_uri:
            logger.warning("No MONGODB_URI found, using in-memory database for testing")
            db.use_memory = True
            return
        
        # Create client
        db.client = AsyncIOMotorClient(mongo_uri)
        
        # Test connection
        await db.client.admin.command('ismaster')
        
        # Get database
        database_name = os.getenv("DATABASE_NAME", "emogo_db")
        db.database = db.client[database_name]
        
        logger.info(f"Connected to MongoDB at {mongo_uri}")
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}, falling back to in-memory database")
        db.use_memory = True


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


async def get_database():
    """Get database instance"""
    try:
        # Check if we should use memory database
        if db.use_memory:
            return "memory_db"  # Special marker for memory database
            
        # Check if database connection exists
        if db.database is None:
            await connect_to_mongo()
            
        if db.use_memory:
            return "memory_db"
            
        return db.database
    except Exception as e:
        logger.error(f"Error getting database: {e}")
        return None

async def get_collection(collection_name: str):
    """Get a collection, either from MongoDB or memory"""
    database = await get_database()
    
    if database == "memory_db":
        return await get_memory_collection(collection_name)
    elif database is None:
        return None
    else:
        return database[collection_name]


# Collection names
VLOGS_COLLECTION = "vlogs"
SENTIMENTS_COLLECTION = "sentiments"
GPS_COLLECTION = "gps_coordinates"
