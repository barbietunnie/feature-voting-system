from fastapi import FastAPI
from app.routes import users, features
from app.core.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Feature Voting System", version="1.0.0")

app.include_router(users.router)
app.include_router(features.router)

@app.get("/")
def read_root():
    return {"message": "Feature Voting System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}