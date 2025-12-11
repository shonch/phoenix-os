# phoenix_engine/utils/create_service_user.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from passlib.context import CryptContext

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "phoenix_engine")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]

def create_service_user(email: str, plain_password: str):
    password_hash = pwd_context.hash(plain_password)
    existing = users_collection.find_one({"email": email})
    if existing:
        print(f"⚠️ User {email} already exists.")
        return
    new_user = {
        "email": email,
        "password_hash": password_hash,
        "role": "service",
    }
    users_collection.insert_one(new_user)
    print(f"✅ Service user {email} created.")

if __name__ == "__main__":
    email = os.getenv("PHOENIX_LOGIN_EMAIL", "service@phoenix")
    plain_password = os.getenv("PHOENIX_LOGIN_PASSWORD", "valhalla_bridge_2025!")
    create_service_user(email, plain_password)
