import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from pymongo import server_api
import logging

logger = logging.getLogger(__name__)

# MongoDB connection will be stored in the FastAPI app instance
# This follows the pattern from the tutorial

async def connect_to_mongo(app):
    """Create database connection and attach to FastAPI app"""
    try:
        # Get MongoDB URI from environment variable
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            # MongoDB Atlas connection for production
            mongo_uri = "mongodb+srv://lairu:emogo2025@cluster0.am8juwb.mongodb.net/?appName=Cluster0"
            logger.info("Using MongoDB Atlas connection.")
        
        # Create client with SSL configuration for Atlas
        app.mongodb_client = AsyncIOMotorClient(
            mongo_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,  # For development/assignment use
            server_api=server_api.ServerApi('1')  # Use Server API v1
        )
        
        # Test connection
        await app.mongodb_client.admin.command('ismaster')
        
        # Get database
        database_name = os.getenv("DATABASE_NAME", "emogo_db")
        app.mongodb = app.mongodb_client[database_name]
        
        logger.info(f"Connected to MongoDB at {mongo_uri}")
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        # Don't raise in startup to allow app to start even without DB
        # This is useful for testing API documentation


async def close_mongo_connection(app):
    """Close database connection"""
    if hasattr(app, 'mongodb_client'):
        app.mongodb_client.close()
        logger.info("Disconnected from MongoDB")


def get_database(app):
    """Get database instance from FastAPI app"""
    if hasattr(app, 'mongodb'):
        return app.mongodb
    else:
        logger.error("Database not connected")
        return None


# Collection names
VLOGS_COLLECTION = "vlogs"
SENTIMENTS_COLLECTION = "sentiments"
GPS_COLLECTION = "gps_coordinates"
