from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.feature import Feature, FeatureCreate, FeatureUpdate
from app.models.feature import Feature as FeatureModel
from app.models.vote import Vote as VoteModel

router = APIRouter(prefix="/api/features", tags=["features"])

@router.post("/", response_model=Feature, status_code=status.HTTP_201_CREATED)
def create_feature(feature: FeatureCreate, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    db_feature = FeatureModel(
        title=feature.title,
        description=feature.description,
        author_id=current_user_id
    )
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

@router.get("/", response_model=List[Feature])
def read_features(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    features = db.query(FeatureModel).order_by(FeatureModel.vote_count.desc()).offset(skip).limit(limit).all()
    return features

@router.get("/{feature_id}", response_model=Feature)
def read_feature(feature_id: int, db: Session = Depends(get_db)):
    db_feature = db.query(FeatureModel).filter(FeatureModel.id == feature_id).first()
    if db_feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")
    return db_feature

@router.put("/{feature_id}", response_model=Feature)
def update_feature(feature_id: int, feature: FeatureUpdate, db: Session = Depends(get_db)):
    db_feature = db.query(FeatureModel).filter(FeatureModel.id == feature_id).first()
    if db_feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")

    for key, value in feature.dict(exclude_unset=True).items():
        setattr(db_feature, key, value)

    db.commit()
    db.refresh(db_feature)
    return db_feature

@router.post("/{feature_id}/vote", response_model=dict, status_code=status.HTTP_201_CREATED)
def vote_feature(feature_id: int, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    feature = db.query(FeatureModel).filter(FeatureModel.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    existing_vote = db.query(VoteModel).filter(
        VoteModel.user_id == current_user_id,
        VoteModel.feature_id == feature_id
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="User has already voted for this feature")

    db_vote = VoteModel(
        user_id=current_user_id,
        feature_id=feature_id
    )
    db.add(db_vote)

    feature.vote_count += 1
    db.commit()

    return {"message": "Vote added successfully", "vote_count": feature.vote_count}

@router.delete("/{feature_id}/vote", status_code=status.HTTP_200_OK)
def remove_vote(feature_id: int, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    feature = db.query(FeatureModel).filter(FeatureModel.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    db_vote = db.query(VoteModel).filter(
        VoteModel.user_id == current_user_id,
        VoteModel.feature_id == feature_id
    ).first()

    if not db_vote:
        raise HTTPException(status_code=404, detail="Vote not found")

    db.delete(db_vote)
    feature.vote_count = max(0, feature.vote_count - 1)
    db.commit()

    return {"message": "Vote removed successfully", "vote_count": feature.vote_count}