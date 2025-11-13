from fastapi import APIRouter
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from schemas.emotion import EmotionFragment

# Load PhoenixOS environment variables
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")

router = APIRouter()

# Connect to MongoDB using .env configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

@router.post("/log_emotion")
def log_emotion(fragment: EmotionFragment):
    # For now, just echo the fragment back
    return {
        "message": "Fragment received.",
        "data": fragment.dict()
    }
