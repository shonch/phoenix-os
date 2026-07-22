# phoenix_portfolio/backend/main.py
# PhoenixOS Emotional Engine
from phoenix_portfolio.backend.routes.classifier_routes import router as classifier_router
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
import os
from pymongo import MongoClient
from phoenix_portfolio.backend.routes.tag_routes import router as tag_router
from pydantic_settings import BaseSettings
from fastapi.middleware.cors import CORSMiddleware
from phoenix_portfolio.backend.routes.auth_routes import router as auth_router

# --- Feature flag for Valhalla ---
class Settings(BaseSettings):
    VALHALLA_ENABLED: bool = True

settings = Settings()

# --- FastAPI app ---
app = FastAPI(title="PhoenixOS Emotional Engine")
app.include_router(classifier_router)
# --- Load environment ---
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=str(ENV_PATH))

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Import PhoenixOS routers (Emotional Engine) ---
from phoenix_portfolio.backend.routes.token_routes import router as token_router
from phoenix_portfolio.backend.routes import phoenix_state_routes

# --- NEW: Unified Ingestion Router ---
from phoenix_portfolio.backend.routes.unified_ingestion_routes import router as unified_router

# --- Include routers ---
# --- Unified Ingestion (PhoenixOS v1) ---
app.include_router(unified_router)

# --- Unified Phoenix State ---
app.include_router(phoenix_state_routes.router)


# --- Tags ---
app.include_router(tag_router)

#authorization 
app.include_router(auth_router)
# --- Try to import Valhalla (optional) ---
if settings.VALHALLA_ENABLED:
    try:
        from emotional_budget_tracker.api.main import router as valhalla_router
        app.include_router(valhalla_router, prefix="/valhalla", tags=["valhalla"])
        print("Valhalla mounted successfully.")
    except Exception as e:
        print(f"Valhalla unavailable: {e}")

# --- Health check ---
@app.get("/health")
def health():
    return {"status": "ok", "service": "phoenix_emotional_engine"}
