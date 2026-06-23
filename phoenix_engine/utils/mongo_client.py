import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConfigurationError

# Load environment variables from .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")              # Primary SRV connection string
MONGO_URI_FALLBACK = os.getenv("MONGO_URI_FALLBACK")  # Direct URI fallback
DB_NAME = os.getenv("DB_NAME")

def get_client():
    """
    Attempt to connect using SRV URI first.
    If SRV fails (e.g., blocked DNS on hotspot), fall back to direct URI.
    """
    try:
        client = MongoClient(MONGO_URI)
        # Force a quick check to confirm connection
        client.admin.command("ping")
        print("Phoenix Engine connected via SRV gateway rune.")
        return client
    except ConfigurationError as e:
        print(f"SRV connection failed: {e}")
        if MONGO_URI_FALLBACK:
            try:
                client = MongoClient(MONGO_URI_FALLBACK)
                client.admin.command("ping")
                print("Phoenix Engine connected via stone path fallback.")
                return client
            except Exception as e2:
                print(f"Fallback connection also failed: {e2}")
                raise
        else:
            raise

# Initialize client and database
client = get_client()
db = client[DB_NAME]

# Example collections (you can expand as needed)
users_collection = db["users"]
fragments_collection = db["emotional_fragments"]
tag_index_collection = db["tag_index"]

# ---------------------------------------------------------
# NEW: Ensure text index exists for search functionality
# ---------------------------------------------------------
try:
    fragments_collection.create_index(
        [
            ("title", "text"),
            ("subject", "text"),
            ("content", "text"),
            ("tags", "text")
        ],
        name="fragment_text_index",
        default_language="english"
    )
    print("Phoenix Engine: text index ensured on emotional_fragments.")
except Exception as e:
    print(f"Phoenix Engine: failed to create text index: {e}")

