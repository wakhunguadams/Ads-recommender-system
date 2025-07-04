from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.ad import PyObjectId # Re-use PyObjectId from ad.py

class UserInteraction(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(..., description="ID of the consumer user")
    ad_id: PyObjectId = Field(..., description="ID of the ad interacted with")
    watch_duration_seconds: Optional[float] = Field(None, ge=0) # For video ads
    completed_watch: bool = False # True if video ad was watched to completion, or banner was viewed sufficiently
    clicked_ad: bool = False # True if user clicked on the ad
    skipped_ad: bool = False # True if user explicitly skipped the ad
    reward_received: bool = False # True if reward was granted for this interaction
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # You can add a 'rating' field if you implement explicit ratings:
    # rating: Optional[int] = Field(None, ge=1, le=5)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}