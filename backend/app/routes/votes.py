from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.vote import Vote, VoteCreate
from app.models.vote import Vote as VoteModel
from app.models.feature import Feature as FeatureModel

router = APIRouter(prefix="/votes", tags=["votes"])

@router.post("/", response_model=Vote, status_code=status.HTTP_201_CREATED)
def create_vote(vote: VoteCreate, current_user_id: int = 1, db: Session = Depends(get_db)):
    existing_vote = db.query(VoteModel).filter(
        VoteModel.user_id == current_user_id,
        VoteModel.feature_id == vote.feature_id
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="User has already voted for this feature")

    db_vote = VoteModel(
        user_id=current_user_id,
        feature_id=vote.feature_id
    )
    db.add(db_vote)

    feature = db.query(FeatureModel).filter(FeatureModel.id == vote.feature_id).first()
    if feature:
        feature.vote_count += 1

    db.commit()
    db.refresh(db_vote)
    return db_vote

@router.delete("/{vote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vote(vote_id: int, current_user_id: int = 1, db: Session = Depends(get_db)):
    db_vote = db.query(VoteModel).filter(
        VoteModel.id == vote_id,
        VoteModel.user_id == current_user_id
    ).first()

    if not db_vote:
        raise HTTPException(status_code=404, detail="Vote not found")

    feature = db.query(FeatureModel).filter(FeatureModel.id == db_vote.feature_id).first()
    if feature:
        feature.vote_count = max(0, feature.vote_count - 1)

    db.delete(db_vote)
    db.commit()

@router.get("/", response_model=List[Vote])
def read_votes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    votes = db.query(VoteModel).offset(skip).limit(limit).all()
    return votes

@router.get("/feature/{feature_id}", response_model=List[Vote])
def read_feature_votes(feature_id: int, db: Session = Depends(get_db)):
    votes = db.query(VoteModel).filter(VoteModel.feature_id == feature_id).all()
    return votes