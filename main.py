from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.mongodb_utils import connect_to_mongo, close_mongo_connection, get_database
from app.api.v1 import recommendations
from app.services.recommendation_service import initialize_recommender
from app.services.data_preprocessing import load_fake_data
import os

# --- Fake Data Generation (for initial setup) ---
def generate_and_load_fake_data():
    # Only load fake data if collections are empty (for initial run)
    db = get_database()
    if db["ads"].count_documents({}) == 0 and db["interactions"].count_documents({}) == 0:
        print("Loading fake data for the first time...")
        # Define paths to your fake data JSON files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fake_ads_path = os.path.join(current_dir, "data", "fake_ads.json")
        fake_user_interactions_path = os.path.join(current_dir, "data", "fake_user_interactions.json")
        load_fake_data(fake_ads_path, fake_user_interactions_path)
    else:
        print("Database already contains data, skipping fake data loading.")


# --- FastAPI Lifespan Events ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    print("FastAPI app starting up...")
    connect_to_mongo()
    generate_and_load_fake_data() # Load fake data on startup
    initialize_recommender() # Initialize recommendation engine
    yield
    # Shutdown event
    print("FastAPI app shutting down...")
    close_mongo_connection()

app = FastAPI(lifespan=lifespan, title="Rewarded Ads Recommendation Engine")

# Include your API routers
app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Rewarded Ads Recommendation Engine API!"}

# How to run the application (from the project root directory):
# uvicorn main:app --reload --port 8001
# (Note: Using port 8001 to avoid conflict with potential Node.js backend on 8000)