from fastapi import APIRouter
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load PhoenixOS environment variables
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

router = APIRouter()

@router.get("/fragments")
def get_fragments(tag: str = None):
    query = {"tags": tag} if tag else {}
    fragments = list(collection.find(query, {"_id": 0}))
    return {"fragments": fragments}

@router.post("/log_emotion")
def log_emotion(fragment: dict):
    collection.insert_one(fragment)
    return {
        "message": "Fragment stored in Phoenix.",
        "data": fragment
    }
