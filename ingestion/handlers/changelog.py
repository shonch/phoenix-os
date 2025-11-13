import re
from datetime import datetime

def parse(content, source_path):
    entries = content.split("## ENTRY START")
    fragments = []

    for entry in entries[1:]:  # Skip anything before first entry
        fragment = {
            "source": source_path,
            "timestamp": None,
            "message": None,
            "tags": [],
            "notes": None,
            "interpretation": None
        }

        # Timestamp
        ts_match = re.search(r"\*\*(\d{4}-\d{2}-\d{2})\*\*", entry)
        if ts_match:
            fragment["timestamp"] = ts_match.group(1)
        else:
            fragment["timestamp"] = datetime.now().isoformat()

        # Message (first paragraph before 'Tag:')
        msg_match = re.search(r"\*\*\d{4}-\d{2}-\d{2}\*\*\n(.*?)\nTag:", entry, re.DOTALL)
        if msg_match:
            fragment["message"] = msg_match.group(1).strip()

        # Tags
        tag_match = re.search(r"Tag:\s*(.*)", entry)
        if tag_match:
            raw_tags = tag_match.group(1)
            cleaned = re.findall(r"`([^`]+)`", raw_tags)
            fragment["tags"] = [tag.strip().strip(",") for tag in cleaned]

        # Notes
        notes_match = re.search(r"Notes:\n(.*)", entry, re.DOTALL)
        if notes_match:
            notes_text = notes_match.group(1).strip()
            notes_text = notes_text.split("## ENTRY END")[0].strip()
            fragment["notes"] = notes_text

        fragments.append(fragment)

    return fragments
