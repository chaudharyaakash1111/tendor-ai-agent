"""
Database connection module for Tender Aggregator.
Supports both MongoDB and PostgreSQL.
"""
import os
from typing import Any, Optional, Union
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db() -> Any:
    """
    Get database connection.
    Defaults to MongoDB, but can be configured for PostgreSQL.
    """
    db_type = os.getenv("DB_TYPE", "mongodb")
    
    if db_type == "postgresql":
        return get_postgres_connection()
    else:
        return get_mongo_connection()

def get_mongo_connection() -> Any:
    """Get MongoDB connection."""
    try:
        # Try to get connection string from environment variable
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/tender_aggregator")
        client = MongoClient(mongo_uri)
        db = client.tender_aggregator
        # Test connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        # Return a mock database for development
        return MockMongoDB()

def get_postgres_connection() -> Any:
    """Get PostgreSQL connection."""
    try:
        # Try to get connection parameters from environment variables
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "tender_aggregator")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            cursor_factory=RealDictCursor
        )
        print("Connected to PostgreSQL successfully")
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

class MockMongoDB:
    """Mock MongoDB for development when no database is available."""
    def __init__(self):
        self.tenders = MockCollection()
    
    def __getitem__(self, name):
        return self.tenders

class MockCollection:
    """Mock MongoDB collection."""
    def __init__(self):
        self.data = []
    
    def delete_many(self, query):
        self.data = []
    
    def insert_many(self, documents):
        self.data.extend(documents)
    
    def find(self, query=None):
        return self.data
    
    def find_one(self, query):
        for item in self.data:
            if all(item.get(k) == v for k, v in query.items()):
                return item
        return None