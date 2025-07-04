from pymongo import MongoClient
from app.core.config import settings

client: MongoClient = None

def connect_to_mongo():
    global client
    client = MongoClient(settings.MONGODB_CONNECTION_STRING)
    print("Connected to MongoDB!")

def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")

def get_database():
    global client
    if client is None:
        raise Exception("MongoDB client not connected. Call connect_to_mongo() first.")
    return client[settings.DATABASE_NAME]