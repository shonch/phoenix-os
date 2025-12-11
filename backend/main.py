# backend/main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
import os
from pymongo import MongoClient
from emotional_budget_tracker.api.main import router as valhalla_router
from backend.routes.emotion_routes import router as emotion_router
from backend.routes.search_routes import router as search_router
from backend.routes.rituals import fragments_router


# 1. Create the FastAPI app first
app = FastAPI(title="PhoenixOS Emotional Engine")

# 2. Load .env from project root
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=str(ENV_PATH))

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# 3. Mount routers AFTER app is defined
app.include_router(valhalla_router, prefix="/valhalla")
app.include_router(emotion_router)
app.include_router(search_router)
app.include_router(fragments_router.router)

# 4. Utility endpoints
@app.get("/")
def read_root():
    return {"message": "PhoenixOS is alive and sovereign."}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/dbcheck")
def dbcheck():
    try:
        db.command("ping")
        return {"status": "connected", "db": db.name}
    except Exception as e:
                return {"status": "error", "detail": str(e)}
