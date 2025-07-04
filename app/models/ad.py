from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

# Custom ObjectId to handle MongoDB's _id
from bson import ObjectId
import pydantic_core
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> pydantic_core.core_schema.CoreSchema:
        return pydantic_core.core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}

    def __str__(self):
        return str(super())

class Ad(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    company_id: str = Field(..., description="ID of the company that uploaded the ad")
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    ad_type: str = Field(..., pattern="^(video|image|banner|app_install)$", description="Type of the ad (video, image, banner, app_install)")
    categories: List[str] = Field(..., description="List of categories the ad belongs to (e.g., 'tech', 'fashion')")
    keywords: List[str] = Field(default_factory=list, description="Keywords extracted from the ad content")
    duration_seconds: Optional[int] = Field(None, ge=5, le=180, description="Duration for video ads in seconds (null for non-video ads)")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    target_audience_demographics: Optional[dict] = None # e.g., {"age_min": 18, "age_max": 35, "gender": "male"}
    ad_creative_url: str = Field(..., description="URL to the ad creative (video/image file)")
    is_active: bool = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
