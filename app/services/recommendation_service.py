import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.data_preprocessing import load_all_ads, load_user_interactions
from typing import List, Dict

# Global variables to store processed data and models (for simplicity; in production, consider caching/more robust loading)
ads_df = None
tfidf_vectorizer = None
ad_content_matrix = None

def initialize_recommender():
    global ads_df, tfidf_vectorizer, ad_content_matrix
    print("Initializing recommender system...")
    ads_df = load_all_ads()

    if ads_df.empty:
        print("No ads found in database. Recommendation engine will return empty results.")
        return

    # Combine relevant text fields for TF-IDF vectorization
    ads_df['combined_text'] = ads_df['title'].fillna('') + " " + \
                              ads_df['description'].fillna('') + " " + \
                              ads_df['categories'].apply(lambda x: " ".join(x) if isinstance(x, list) else "") + " " + \
                              ads_df['keywords'].apply(lambda x: " ".join(x) if isinstance(x, list) else "")

    tfidf_vectorizer = TfidfVectorizer(stop_words='english', min_df=1, max_features=5000)
    ad_content_matrix = tfidf_vectorizer.fit_transform(ads_df['combined_text'])
    print("Recommender system initialized.")


def get_content_based_recommendations(user_id: str, num_recommendations: int = 10) -> List[Dict]:
    if ads_df is None or tfidf_vectorizer is None or ad_content_matrix is None:
        initialize_recommender() # Ensure recommender is initialized

    if ads_df.empty:
        return []

    # Get user's watched ads
    user_interactions = load_user_interactions(user_id)
    # Filter for ads the user completed watching or clicked
    engaged_ad_ids = user_interactions[(user_interactions['completed_watch'] == True) | (user_interactions['clicked_ad'] == True)]['ad_id'].tolist()

    if not engaged_ad_ids:
        # Cold start for new users or users with no engagement: recommend popular/random ads
        # For a real system, you'd have a more sophisticated popularity/diversity fallback
        print(f"User {user_id} has no engaged ads. Returning top 10 general ads.")
        result = ads_df.head(num_recommendations).to_dict(orient='records')
        
        # Replace NaN values with None for JSON serialization
        import math
        for ad in result:
            for key, value in ad.items():
                if isinstance(value, float) and math.isnan(value):
                    ad[key] = None
        return result


    # Get content features of engaged ads
    # Ensure ad_id from interactions matches _id in ads_df (both as strings)
    engaged_ads_df = ads_df[ads_df['_id'].isin(engaged_ad_ids)]

    if engaged_ads_df.empty:
        # Fallback if engaged ads are not found in the current ads_df (e.g., ad removed)
        print(f"No active ads found for user's engaged ad IDs {engaged_ad_ids}. Returning top 10 general ads.")
        result = ads_df.head(num_recommendations).to_dict(orient='records')
        
        # Replace NaN values with None for JSON serialization
        import math
        for ad in result:
            for key, value in ad.items():
                if isinstance(value, float) and math.isnan(value):
                    ad[key] = None
        return result


    engaged_ads_features = tfidf_vectorizer.transform(engaged_ads_df['combined_text'])

    # Create a user profile by averaging the TF-IDF vectors of engaged ads
    user_profile = engaged_ads_features.mean(axis=0)
    
    # Convert sparse matrices to dense arrays for compatibility with newer scikit-learn
    user_profile_array = user_profile.toarray() if hasattr(user_profile, 'toarray') else np.asarray(user_profile)
    ad_content_matrix_array = ad_content_matrix.toarray() if hasattr(ad_content_matrix, 'toarray') else np.asarray(ad_content_matrix)

    # Calculate cosine similarity between user profile and all ads
    similarity_scores = cosine_similarity(user_profile_array, ad_content_matrix_array)
    
    # Create a DataFrame for easy sorting and filtering
    # Ensure ads_df['_id'] is aligned with the similarity scores
    similarity_df = pd.DataFrame({
        'ad_id': ads_df['_id'],
        'similarity': similarity_scores.flatten()
    })

    # Filter out ads already watched/engaged by the user
    unwatched_ads_scores = similarity_df[~similarity_df['ad_id'].isin(engaged_ad_ids)]

    # Sort by similarity and get top N recommendations
    recommended_ad_ids = unwatched_ads_scores.sort_values(by='similarity', ascending=False).head(num_recommendations)['ad_id'].tolist()

    # Fetch full details of recommended ads
    recommended_ads_details = ads_df[ads_df['_id'].isin(recommended_ad_ids)]
    
    # Convert to dict and handle NaN values
    result = recommended_ads_details.to_dict(orient='records')
    
    # Replace NaN values with None for JSON serialization
    import math
    for ad in result:
        for key, value in ad.items():
            if isinstance(value, float) and math.isnan(value):
                ad[key] = None
    
    return result

# Function for updating models - could be triggered periodically or via an admin endpoint
def update_recommender_models():
    print("Updating recommender models...")
    initialize_recommender() # Re-load data and retrain TF-IDF
    print("Recommender models updated.")
