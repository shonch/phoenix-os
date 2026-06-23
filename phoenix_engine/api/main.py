# phoenix_engine/api/main.py
# Phoenix Engine — Identity Altar

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from bson import ObjectId
import os
from dotenv import load_dotenv

# 🌐 Load environment
load_dotenv()

# 🔐 Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📂 Mongo connector (canonical path)
from phoenix_engine.utils.mongo_client import users_collection

# ⭐ Shared JWT auth (Phoenix v2)
from phoenix_portfolio.phoenix_platform.auth import (
    verify_token,
    create_access_token,
)

# 🚀 FastAPI app
app = FastAPI(title="Phoenix Engine")

# 📦 Token response model
class Token(BaseModel):
    access_token: str
    token_type: str

# 🔐 Password helpers
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

# 🌡 Health check
@app.get("/health")
def health():
    return {"status": "ok", "service": "phoenix"}

# 🔐 Login route — checks MongoDB users collection
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = create_access_token(data={"sub": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

# 👤 Protected route — returns user info
@app.get("/users/me")
async def users_me(user_id: str = Depends(verify_token)):
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user id"
        )
    user = users_collection.find_one({"_id": oid})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user["_id"] = str(user["_id"])
    return user

# 🌌 Mythic heartbeat
@app.get("/")
def read_root():
    return {"message": "Phoenix Engine is alive, sovereign, and rising as cathedral."}

# 📎 Routers (import at the end to avoid circulars)
from .users_router import router as users_router
from .tags_router import router as tags_router

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(tags_router)

