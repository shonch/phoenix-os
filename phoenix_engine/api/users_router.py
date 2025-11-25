# phoenix_engine/api/users_router.py
# Unified Identity Router — Phoenix Engine
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt, JWTError
from bson import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer


# --- Environment ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
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
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")

# --- Endpoints ---
@router.post("/", response_model=UserOut)
async def create_user(user: UserCreate):
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    doc = {
        "email": user.email,
        "username": user.username,
        "password_hash": hashed_pw,
        "archetype": user.archetype,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(doc)
    return UserOut(
        id=str(result.inserted_id),
        email=user.email,
        username=user.username,
        archetype=user.archetype,
    )

@router.post("/login", response_model=Token)
async def login(user: UserCreate):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": str(db_user["_id"])}, expires_delta=token_expires)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/{id}", response_model=UserOut)
async def read_user(id: str, current_user: dict = Depends(get_current_user)):
    if str(current_user["_id"]) != id and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Not authorized")
    user = await db.users.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(
        id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        archetype=user.get("archetype"),
    )

@router.put("/{id}", response_model=UserOut)
async def update_user(id: str, update: UserUpdate, current_user: dict = Depends(get_current_user)):
    if str(current_user["_id"]) != id and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Not authorized")
    updates = {k: v for k, v in update.dict().items() if v is not None}
    result = await db.users.update_one({"_id": ObjectId(id)}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    user = await db.users.find_one({"_id": ObjectId(id)})
    return UserOut(
        id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        archetype=user.get("archetype"),
    )

@router.delete("/{id}")
async def delete_user(id: str, current_user: dict = Depends(get_current_user)):
    if str(current_user["_id"]) != id and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}
