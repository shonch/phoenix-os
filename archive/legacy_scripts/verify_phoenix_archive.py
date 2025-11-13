from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB using Phoenix credentials
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["fragments"]  # Update if your collection name is different

# List of emotionally authored files to verify (Valhalla excluded)
emotionally_authored_files = [
    "./Phoenix/index.md",
    "./Phoenix/emotional_logs/emotional_changelog.md",
    "./Phoenix/emotional_logs/ache_architect.md",
    "./Phoenix/emotional_logs/emerge_log.txt",
    "./Phoenix/emotional_logs/emotional_log.txt",
    "./Phoenix/emotional_logs/detective_log.txt",
    "./Phoenix/rituals/tag_index.txt",
    "./Phoenix/rituals/archive_log.txt",
    "./Phoenix/rituals/README.md",
    "./Phoenix/phoenix_inspect_menu.py",
    "./Phoenix/frisson_journal/entries/2025-08-24-17-54-EDT.md",
    "./Phoenix/frisson_journal/entries/2025-08-24-runner-lightning.md",
    "./Phoenix/frisson_journal/entries/2025-08-31-evening-release.md",
    "./Phoenix/frisson_journal/entries/2025-09-02-signal-mapped.md",
    "./Phoenix/frisson_journal/entries/2025-09-06-18-24.md",
    "./Phoenix/frisson_journal/entries/2025-09-03-false_signal.md",
    "./Phoenix/frisson_journal/entries/last_clipboard.txt",
    "./Phoenix/frisson_journal/entries/2025-08-27-Cabin Dream: Bruce, the Call, and the Trailer That Waits.md",
    "./Phoenix/frisson_journal/tags/kinetic_awe.txt",
    "./Phoenix/frisson_journal/tags/silent_recognition.txt",
    "./Phoenix/frisson_journal/README.md",
    "./Phoenix/frisson_journal/pulses/2025-09-09-1717-Exit Mapped, Craving Redirected, Presence Held.md",
    "./Phoenix/frisson_journal/pulses/2025-08-24-1640-yaz shimmer, late afternoon.md",
    "./Phoenix/frisson_journal/budget/2025-09-02-Clothing purchase for emotional recalibration.md",
    "./Phoenix/frisson_journal/budget/2025-09-02-Upwork Profile launch.md",
    "./memoir/fragments/ache_architect.md",
    "./Documents/emotional_tracker/emotional_tracker.md",
    "./refactor_log.txt",
    "./deletion_log_20250822_140041.txt",
    "./inspect_tag_index.py",
    "./tag_migration.py",
    "./ritual_finance.py"
]

# Sweep and log results
found = []
missing = []

for path in emotionally_authored_files:
    result = collection.find_one({"source_path": path})
    if result:
        found.append(path)
    else:
        missing.append(path)

# Output results
print("✅ Archived in Phoenix:")
for f in found:
    print(f"  - {f}")

print("\n❌ Missing from Phoenix:")
for f in missing:
    print(f"  - {f}")
