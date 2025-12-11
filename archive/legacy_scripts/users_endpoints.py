# users_endpoints.py — Sovereign Identity Endpoints
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# --- Environment setup ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("API_KEY")  # or a dedicated JWT secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

client = AsyncIOMotorClient(MONGO_URI)
db = client.phoenix_engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


# --- Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    archetype: str | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    archetype: str | None = None


class UserOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    archetype: str | None


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Helpers ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- Endpoints ---
@router.post("/", response_model=UserOut)
async def create_user(user: UserCreate):
    try:
        existing = await db.users.find_one({"email": user.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = hash_password(user.password)
        new_user = {
            "email": user.email,
            "username": user.username,
            "password": hashed_pw,
            "archetype": user.archetype,
        }
        result = await db.users.insert_one(new_user)
        return {
            "id": str(result.inserted_id),
            "email": user.email,
            "username": user.username,
            "archetype": user.archetype,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ObjectId endpoints ---
@router.get("/{id}", response_model=UserOut)
async def read_user(id: str):
    try:
        user = await db.users.find_one({"_id": ObjectId(id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "archetype": user.get("archetype"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id}", response_model=UserOut)
async def update_user(id: str, update: UserUpdate):
    try:
        updates = {k: v for k, v in update.dict().items() if v is not None}
        result = await db.users.update_one({"_id": ObjectId(id)}, {"$set": updates})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        user = await db.users.find_one({"_id": ObjectId(id)})
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "archetype": user.get("archetype"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}")
async def delete_user(id: str):
    try:
        result = await db.users.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Username endpoints ---
@router.get("/by-username/{username}", response_model=UserOut)
async def read_user_by_username(username: str):
    try:
        user = await db.users.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "archetype": user.get("archetype"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/by-username/{username}", response_model=UserOut)
async def update_user_by_username(username: str, update: UserUpdate):
    try:
        updates = {k: v for k, v in update.dict().items() if v is not None}
        result = await db.users.update_one({"username": username}, {"$set": updates})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        user = await db.users.find_one({"username": username})
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "archetype": user.get("archetype"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/by-username/{username}")
async def delete_user_by_username(username: str):
    try:
        result = await db.users.delete_one({"username": username})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": f"User '{username}' deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Login ---
@router.post("/login", response_model=Token)
async def login(user: UserCreate):
    try:
        db_user = await db.users.find_one({"email": user.email})
        if not db_user or not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": str(db_user["_id"])}, expires_delta=token_expires
        )
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
