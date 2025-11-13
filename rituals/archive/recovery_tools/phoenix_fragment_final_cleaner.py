# phoenix_fragment_final_cleaner.py — Remove Verified Skipped Notes
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

# Load environment
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["fragments"]

# Target fragment
fragment_id = ObjectId("68f7d2391a5c0c06e3d90203")
fragment = collection.find_one({"_id": fragment_id})

if not fragment or "notes" not in fragment:
    print("⚠️ Fragment not found or missing notes.")
    exit()

notes = fragment["notes"]

# ✅ Recovered paths to remove
recovered_paths = [
    "/Users/shonheersink/Phoenix/Oslo Positioning Plan - AI-n_Native Transition/Oslo_Positioning_Plan_—_AI-Native_Transition.md",
    "/Users/shonheersink/Phoenix/decompression/Decompression_Ritual_Options.md",
    "/Users/shonheersink/Phoenix/oslo_strategy/Lagos_Opportunities.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/detective.sh_concept.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/emotional_budget_tracker_code_placeholder.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/Idea_Repository_-_Rituals_and_Sacred_Tasks.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/ingestion/log.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/rituals/launcher/README.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/rituals/README.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/window_of_wonder.md.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/Phoenix_Portfoli_Ritual_-_October_Launch.md",
    "/Users/shonheersink/Phoenix/code_fragments/main.py_-_emotional_budget_tracker_(draft).md",
    "/Users/shonheersink/Phoenix/README.md",
    "/Users/shonheersink/Phoenix/index.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-24-17-54-EDT.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-24-runner-lightning.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-09-02-signal-mapped.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-09-06-18-24.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-09-03-false_signal.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-27-Cabin Dream: Bruce, the Call, and the Trailer That Waits.md",
    "/Users/shonheersink/Phoenix/frisson_journal/README.md",
    "/Users/shonheersink/Phoenix/frisson_journal/pulses/2025-09-09-1717-Exit Mapped, Craving Redirected, Presence Held.md",
    "/Users/shonheersink/Phoenix/frisson_journal/pulses/2025-08-24-1640-yaz shimmer, late afternoon.md",
    "/Users/shonheersink/Phoenix/frisson_journal/budget/2025-09-02-Clothing purchase for emotional recalibration.md",
    "/Users/shonheersink/Phoenix/frisson_journal/budget/2025-09-02-Upwork Profile launch.md",
    "/Users/shonheersink/Phoenix/training_strategy/emotional_budget_tracker_schema_sketch.md.md",
    "/Users/shonheersink/Phoenix/rituals/archive/README.md",
    "/Users/shonheersink/Phoenix/rituals/README.md",
    "/Users/shonheersink/Phoenix/rituals/.md",
    "/Users/shonheersink/Phoenix/emotional_logs/ache_architect.md",
    "/Users/shonheersink/memoir/fragments/ache_architect.md",
    "/Users/shonheersink/frisson_journal/entries/.md",
    "/Users/shonheersink/frisson_journal/outreach/2025-09-02-Upwork Profile.md",
    "/Users/shonheersink/git_repos/active/emotional_budget_tracker/README.md",
    "/Users/shonheersink/git_repos/active/emotional_budget_tracker/rituals/README.md"
]

# Remove each skipped line
for path in recovered_paths:
    skipped_line = f"- ❓ Unknown format skipped: {path}\n"
    notes = notes.replace(skipped_line, "")

# Update fragment
collection.update_one({"_id": fragment_id}, {"$set": {"notes": notes}})
print("🧹 Final sweep complete. All verified skipped notes removed.")
