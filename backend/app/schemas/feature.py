from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class FeatureBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Feature title")
    description: str = Field(..., min_length=10, max_length=1000, description="Feature description")

class FeatureCreate(FeatureBase):
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty or just whitespace')
        return v.strip()

class FeatureUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    vote_count: Optional[int] = None

class Feature(FeatureBase):
    id: int
    author_id: int
    created_at: datetime
    vote_count: int

    class Config:
        from_attributes = True