# phoenix_engine/api/users_router.py
# Phoenix Engine — User Management Module
# Author: Shon Heersink & Copilot

from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from phoenix_engine.utils.mongo_client import users_collection
from phoenix_engine.models.user import User
from passlib.context import CryptContext
from typing import List
from datetime import datetime

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📦 Create user
@router.post("/", response_model=User, status_code=201)
def create_user(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "password_hash": pwd_context.hash(user.password_hash),
        "roles": user.roles or ["user"],
        "created_at": datetime.utcnow(),
        "note": user.note,
    }
    inserted = users_collection.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    return User(**doc)

# 📖 Read user
@router.get("/{user_id}", response_model=User)
def read_user(user_id: str):
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return User(**user)

# ✏️ Update user
@router.put("/{user_id}", response_model=User)
def update_user(user_id: str, update: User):
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_doc = update.dict(exclude_unset=True)
    if "password_hash" in update_doc:
        update_doc["password_hash"] = pwd_context.hash(update_doc["password_hash"])
    users_collection.update_one({"user_id": user_id}, {"$set": update_doc})
    updated = users_collection.find_one({"user_id": user_id})
    updated["_id"] = str(updated["_id"])
    return User(**updated)

# 🗑 Delete user
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str):
    result = users_collection.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return None
