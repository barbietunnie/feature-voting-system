from pydantic import BaseModel
from datetime import datetime

class VoteBase(BaseModel):
    feature_id: int

class VoteCreate(VoteBase):
    pass

class Vote(VoteBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True