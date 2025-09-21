from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FeatureBase(BaseModel):
    title: str
    description: str

class FeatureCreate(FeatureBase):
    pass

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