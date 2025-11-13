from pymongo import MongoClient
import os
from dotenv import load_dotenv

import re

# Load .env from phoenix_portfolio
load_dotenv(dotenv_path=".env")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["fragments"]

def clean_text(text):
    """Sanitize text for filename use."""
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', '_', text)      # Replace spaces with underscores
    return text[:60]  # Limit length for safety

# Find all documents with missing filename
nameless_docs = collection.find({"filename": None})
updated_count = 0

for doc in nameless_docs:
    source = doc.get("source", "")
    notes = doc.get("notes", "")

    # Extract base name from source path
    source_name = os.path.basename(source).replace(".md", "").replace(".txt", "")
    source_name = clean_text(source_name) if source_name else "unnamed"

    # Extract first phrase from notes
    notes_snippet = notes.split(".")[0] if notes else "no_notes"
    notes_name = clean_text(notes_snippet)

    # Combine into hybrid filename
    hybrid_filename = f"{source_name}__{notes_name}.md"

    # Update document
    result = collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"filename": hybrid_filename}}
    )

    if result.modified_count > 0:
        updated_count += 1
        print(f"Updated: {hybrid_filename}")

print(f"\nTotal filenames restored: {updated_count}")
