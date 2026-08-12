# phoenix_portfolio/backend/routes/auth_routes.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime
from phoenix_platform.auth import create_access_token, create_refresh_token, verify_refresh_token
from backend.mongo_client import db
from phoenix_platform.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_collection = db["users"]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    refresh_token: str
    email: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest):
    existing = users_collection.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    doc = {
        "email": payload.email,
        "username": payload.username or payload.email.split("@")[0],
        "password_hash": pwd_context.hash(payload.password),
        "created_at": datetime.utcnow(),
    }
    users_collection.insert_one(doc)

    # user_id (the "sub" claim) is the email itself — matches every existing
    # route/engine/builder across the app, which all query Mongo by email string.
    token = create_access_token({"sub": payload.email})
    refresh = create_refresh_token({"sub": payload.email})
    return {"token": token, "refresh_token": refresh, "email": payload.email}

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    user = users_collection.find_one({"email": payload.email})
    if not user or not pwd_context.verify(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token({"sub": payload.email})
    refresh = create_refresh_token({"sub": payload.email})
    return {"token": token, "refresh_token": refresh, "email": payload.email}


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(payload: RefreshRequest):
    email = verify_refresh_token(payload.refresh_token)
    new_token = create_access_token({"sub": email})
    new_refresh = create_refresh_token({"sub": email})
    return {"token": new_token, "refresh_token": new_refresh, "email": email}
