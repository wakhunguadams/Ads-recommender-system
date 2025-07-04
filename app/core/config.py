import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Settings:
    PROJECT_NAME: str = "Rewarded Ads Recommender"
    MONGODB_CONNECTION_STRING: str = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "rewarded_ads_db")

settings = Settings()