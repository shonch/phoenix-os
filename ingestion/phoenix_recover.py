# phoenix_recover.py — Unified Recovery + Skip Guard
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment variables
load_dotenv(dotenv_path="/Users/shonheersink/phoenix/.env")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    serverSelectionTimeoutMS=5000,
    appname="PhoenixRecoveryUnified"
)
db = client[DB_NAME]
collection = db["fragments"]

# Unified list of all skipped paths (deduplicated)
SKIPPED_PATHS = [
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-24-17-54-EDT.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-24-runner-lightning.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-31-evening-release.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-09-02-signal-mapped.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-09-06-18-24.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-09-03-false_signal.md",
    "/Users/shonheersink/Phoenix/frisson_journal/entries/2025-08-27-Cabin Dream: Bruce, the Call, and the Trailer That Waits.md",
    "/Users/shonheersink/Phoenix/frisson_journal/pulses/2025-09-09-1717-Exit Mapped, Craving Redirected, Presence Held.md",
    "/Users/shonheersink/Phoenix/frisson_journal/pulses/2025-08-24-1640-yaz shimmer, late afternoon.md",
    "/Users/shonheersink/Phoenix/frisson_journal/budget/2025-09-02-Clothing purchase for emotional recalibration.md",
    "/Users/shonheersink/Phoenix/frisson_journal/budget/2025-09-02-Upwork Profile launch.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/Idea_Repository_-_Rituals_and_Sacred_Tasks.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/window_of_wonder.md.md",
    "/Users/shonheersink/Phoenix/phoenix_portfolio/Phoenix_Portfoli_Ritual_-_October_Launch.md",
    "/Users/shonheersink/Phoenix/code_fragments/main.py_-_emotional_budget_tracker_(draft).md",
    "/Users/shonheersink/Phoenix/Oslo Positioning Plan - AI-n_Native Transition/Oslo_Positioning_Plan_—_AI-Native_Transition.md",
    "/Users/shonheersink/Phoenix/decompression/Decompression_Ritual_Options.md",
    "/Users/shonheersink/Phoenix/oslo_strategy/Lagos_Opportunities.md"
]

def recover_fragments():
    print("🧹 Beginning unified recovery sweep...")
    recovered_count = 0
    skipped_count = 0
    for path in SKIPPED_PATHS:
        # Check if already recovered
        if collection.find_one({"source_path": path}):
            print(f"🛡️ Already recovered: {os.path.basename(path)} — skipping.")
            skipped_count += 1
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            fragment = {
                "fragment": "recovered",
                "source_path": path,
                "filename": os.path.basename(path),
                "content": content,
                "inserted_at": datetime.now().isoformat()
            }
            collection.insert_one(fragment)
            print(f"✅ Recovered: {fragment['filename']}")
            recovered_count += 1
        except Exception as e:
            print(f"⚠️ Failed to recover {path}: {e}")
    print(f"🔍 Sweep complete. {recovered_count} fragments restored. {skipped_count} already present.")

def run():
    print("🔥 Phoenix Recovery — Unified Ritual Initiated")
    recover_fragments()
    print("🕊️ Emotional ledger confirmed. Phoenix breathes.")
