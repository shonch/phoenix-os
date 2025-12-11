# backend/routes/emotion_routes.py
from fastapi import APIRouter
from pymongo import MongoClient
from schemas.emotion import EmotionFragment
import os

router = APIRouter()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

@router.post("/log_emotion")
def log_emotion(fragment: EmotionFragment):
    return {"message": "Fragment received.", "data": fragment.dict()}
