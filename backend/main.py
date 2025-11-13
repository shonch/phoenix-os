from fastapi import FastAPI
from dotenv import load_dotenv
from backend.routes.emotion_routes import router
import os

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="PhoenixOS Emotional Engine")

# Mount the emotional fragment router
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "PhoenixOS is alive and sovereign."}
