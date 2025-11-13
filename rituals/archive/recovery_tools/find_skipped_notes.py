from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["fragments"]

echo_fragments = []

# Step 1: Find all fragments with skipped echoes
for doc in collection.find({}):
    notes = doc.get("notes", "")
    if "❓ Unknown format skipped:" in notes:
        echo_fragments.append({
            "_id": str(doc["_id"]),
            "preview": "\n".join(notes.splitlines()[:5]) + "\n..."
        })

# Step 2: Print them
print(f"\n🔍 Found {len(echo_fragments)} fragments with skipped echoes:\n")
for frag in echo_fragments:
    print(f"🧱 Fragment ID: {frag['_id']}")
    print(f"{frag['preview']}")
    print("—" * 40)

# Optional: Ask to purge
confirm = input("\nDo you want to overwrite ALL of them with clean notes? (yes/no): ")
if confirm.lower() == "yes":
    for frag in echo_fragments:
        collection.update_one(
            {"_id": {"$regex": frag["_id"]}},
            {"$set": {"notes": "🧹 All skipped fragments recovered. Emotional integrity restored."}}
        )
    print("\n✅ All echo fragments overwritten. The ghosts are gone.")
else:
    print("\n🛑 No changes made. Echoes still remain.")
