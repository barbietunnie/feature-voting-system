from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.routes import users, features
from app.core.database import engine, Base
from app.core.exceptions import (
    validation_exception_handler,
    integrity_error_handler,
    feature_voting_exception_handler,
    http_exception_handler,
    generic_exception_handler,
    FeatureVotingException
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Feature Voting System", version="1.0.0")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(FeatureVotingException, feature_voting_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(users.router)
app.include_router(features.router)

@app.get("/")
def read_root():
    return {"message": "Feature Voting System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}