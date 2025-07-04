from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from app.services.recommendation_service import get_content_based_recommendations, update_recommender_models
from app.models.ad import Ad # Import your Ad Pydantic model

router = APIRouter()

@router.get("/recommendations/{user_id}", response_model=List[Ad])
async def get_user_recommendations(user_id: str, num_ads: int = 10):
    """
    Get recommended ads for a specific user.
    """
    recommendations = get_content_based_recommendations(user_id, num_ads)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found for this user or no ads available.")
    return recommendations

@router.post("/recommendations/train")
async def train_recommendation_model():
    """
    Trigger the training/update of the recommendation model.
    (This would ideally be an admin-only endpoint or scheduled task)
    """
    update_recommender_models()
    return {"message": "Recommendation model update initiated successfully."}
