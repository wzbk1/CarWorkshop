from pydantic import BaseModel, Field
from datetime import datetime


class ReviewCreate(BaseModel):
    location_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)


class ReviewResponse(BaseModel):
    id: int
    user_email: str
    user_name: str
    location_id: int
    rating: int
    comment: str | None
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ReviewStatsResponse(BaseModel):
    location_id: int
    average_rating: float
    total_reviews: int