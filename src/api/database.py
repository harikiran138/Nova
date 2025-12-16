from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from src.agent_core.config import Config

_client = None

def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        config = Config.from_env()
        # Ensure we have a valid URI
        if not config.mongodb_uri:
             raise ValueError("MONGODB_URI is not set in configuration")
        _client = MongoClient(config.mongodb_uri)
    return _client

def get_database() -> Database:
    client = get_mongo_client()
    config = Config.from_env()
    return client[config.mongodb_db_name]

def get_collection() -> Collection:
    db = get_database()
    config = Config.from_env()
    return db[config.mongodb_collection_name]
