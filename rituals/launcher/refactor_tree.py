# 🌲 Digital Excavation – Phase 1 (Python Edition)
# Author: Shon Heersink (with Copilot)
# Date: October 25, 2025

import os
from datetime import datetime
from pathlib import Path

# Define base paths
home = Path.home()
log_path = home / "Documents" / "refactor_log.txt"

# Create destination folders
destinations = {
    "Archive/Legacy": [
        "2023 tax docs", "C188", "C194 writing", "C951", "C960 files", "C964", "Cognizant"
    ],
    "Projects/Code": [
        "c++", "c++ review", "C960 Project (Python)"
    ],
    "Identity/Artifacts": [
        "certificates", "GallupReport.pdf", "project screenshots"
    ],
    "Compost/ReviewLater": [
        "$RECYCLE.BIN"
    ]
}

# Ensure destination folders exist
for folder in destinations:
    path = home / "Documents" / folder
    path.mkdir(parents=True, exist_ok=True)

# Move function with emotional logging
def move_if_exists(source_name, dest_folder):
    source = home / "Documents" / source_name
    destination = home / "Documents" / dest_folder / source.name

    if source.exists():
        try:
            source.rename(destination)
            log_entry = f"Moved {source.name} to {dest_folder} – {datetime.now()}\n"
        except Exception as e:
            log_entry = f"⚠️ Error moving {source.name}: {e}\n"
    else:
        log_entry = f"⚠️ Skipped: {source} not found\n"

    with open(log_path, "a") as log_file:
        log_file.write(log_entry)

# Ritual execution
for dest_folder, items in destinations.items():
    for item in items:
        move_if_exists(item, dest_folder)

# Completion message
print("Refactor complete. Emotional architecture updated. Log saved to ~/Documents/refactor_log.txt")
