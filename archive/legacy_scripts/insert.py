from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(dotenv_path=".env")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["fragments"]

# Load the markdown content
file_path = "../Oslo Positioning Plan - AI-n_Native Transition/Oslo_Positioning_Plan_—_AI-Native_Transition.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Prepare the document
doc = {
    "filename": "Oslo_Positioning_Plan_AI-Native_Transition.md",
    "source": file_path,
    "tags": ["oslo", "ai_native", "emotional_ux", "legacy_integration", "rebirth", "readiness_strategy"],
    "message": "Oslo Readiness Strategy — bridging legacy systems and agentic AI",
    "notes": content,
    "timestamp": "2025-11-10",
    "inserted_at": datetime.utcnow().isoformat()
}

# Insert into MongoDB
result = collection.insert_one(doc)
print(f"Inserted with ID: {result.inserted_id}")
