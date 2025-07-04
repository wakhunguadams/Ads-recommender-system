import pandas as pd
from app.db.mongodb_utils import get_database
from typing import List, Dict
from bson import ObjectId # For converting ObjectId to string if needed

def load_all_ads() -> pd.DataFrame:
    db = get_database()
    ads_cursor = db["ads"].find({})
    ads_list = []
    for ad in ads_cursor:
        ad['_id'] = str(ad['_id']) # Convert ObjectId to string for Pandas
        # Handle None/null values properly for duration_seconds
        if ad.get('duration_seconds') is None:
            ad['duration_seconds'] = None
        ads_list.append(ad)
    df = pd.DataFrame(ads_list)
    
    # Replace any NaN values with None for proper JSON serialization
    df = df.where(pd.notnull(df), None)
    
    return df

def load_user_interactions(user_id: str = None) -> pd.DataFrame:
    db = get_database()
    query = {}
    if user_id:
        query["user_id"] = user_id
    interactions_cursor = db["interactions"].find(query)
    interactions_list = []
    for interaction in interactions_cursor:
        interaction['_id'] = str(interaction['_id'])
        interaction['ad_id'] = str(interaction['ad_id']) # Ensure ad_id is string
        interactions_list.append(interaction)
    return pd.DataFrame(interactions_list)

def load_fake_data(ads_path: str, interactions_path: str):
    # This function is for initial setup with fake JSON files
    # In production, this data would primarily come from MongoDB
    import json

    with open(ads_path, 'r') as f:
        fake_ads = json.load(f)
    # Convert _id to ObjectId type for insertion if they are strings in JSON
    for ad in fake_ads:
        if '_id' in ad and isinstance(ad['_id'], str):
            ad['_id'] = ObjectId(ad['_id'])

    with open(interactions_path, 'r') as f:
        fake_interactions = json.load(f)
    # Convert _id and ad_id to ObjectId type for insertion if they are strings in JSON
    for interaction in fake_interactions:
        if '_id' in interaction and isinstance(interaction['_id'], str):
            interaction['_id'] = ObjectId(interaction['_id'])
        if 'ad_id' in interaction and isinstance(interaction['ad_id'], str):
            interaction['ad_id'] = ObjectId(interaction['ad_id'])


    db = get_database()
    db["ads"].insert_many(fake_ads)
    db["interactions"].insert_many(fake_interactions)
    print("Fake data loaded into MongoDB!")

# Note: For asynchronous MongoDB operations with FastAPI, you would typically use an async driver like `motor`.
# The `pymongo` driver is synchronous by default, which can block the FastAPI event loop.
# For simplicity with fake data and demonstration, we'll use `pymongo` here, but for production,
# switch to `motor` and use `await` with its operations.
# For the purpose of this demo, we'll manually use `async for` with `pymongo`'s cursor, but
# a proper `motor` setup is preferred.