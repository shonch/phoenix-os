from passlib.context import CryptContext
import sys
sys.path.insert(0, "/Users/shonheersink/Phoenix/phoenix_portfolio")
from backend.mongo_client import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

kristen_email = "pheauxpheaux@gmail.com"
temp_password = "Welcome1"

new_hash = pwd_context.hash(temp_password)

users = db["users"]
result = users.update_one(
    {"email": kristen_email},
    {"$set": {"password_hash": new_hash}}
)

print("Matched:", result.matched_count, "Modified:", result.modified_count)
print("Temp password to give Kristen:", temp_password)
