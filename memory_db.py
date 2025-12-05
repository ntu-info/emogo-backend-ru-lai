"""
In-memory data storage for testing when MongoDB is not available
"""
from datetime import datetime
from typing import List, Dict, Any
import json

class InMemoryDatabase:
    def __init__(self):
        self.collections = {
            "vlogs": [],
            "sentiments": [], 
            "gps_coordinates": []
        }
        self.next_id = 1
    
    async def insert_one(self, collection: str, document: Dict[Any, Any]):
        """Insert a document into a collection"""
        document["_id"] = str(self.next_id)
        self.next_id += 1
        self.collections[collection].append(document)
        return MockResult(document["_id"])
    
    async def find(self, collection: str, query: Dict[Any, Any] = None, skip: int = 0, limit: int = None):
        """Find documents in a collection"""
        docs = self.collections.get(collection, [])
        if skip > 0:
            docs = docs[skip:]
        if limit:
            docs = docs[:limit]
        return docs
    
    async def count_documents(self, collection: str, query: Dict[Any, Any] = None):
        """Count documents in a collection"""
        return len(self.collections.get(collection, []))

class MockResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

# Global in-memory database instance
memory_db = InMemoryDatabase()

async def get_memory_collection(collection_name: str):
    """Get a collection from memory database"""
    return MemoryCollection(collection_name)

class MemoryCollection:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
    
    async def insert_one(self, document: Dict[Any, Any]):
        return await memory_db.insert_one(self.collection_name, document)
    
    def find(self, query: Dict[Any, Any] = None):
        return MemoryCursor(self.collection_name, query)
    
    async def count_documents(self, query: Dict[Any, Any] = None):
        return await memory_db.count_documents(self.collection_name, query)

class MemoryCursor:
    def __init__(self, collection_name: str, query: Dict[Any, Any] = None):
        self.collection_name = collection_name
        self.query = query
        self.skip_count = 0
        self.limit_count = None
    
    def skip(self, count: int):
        self.skip_count = count
        return self
    
    def limit(self, count: int):
        self.limit_count = count
        return self
    
    async def __aiter__(self):
        docs = await memory_db.find(self.collection_name, self.query, self.skip_count, self.limit_count)
        for doc in docs:
            yield doc
