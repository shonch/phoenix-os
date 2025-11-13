import re
from utils import extract_tags_notes

def parse(file_path):
    fragments = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract timestamp from filename
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}[-_]\d{2}[-_]\d{2})', file_path)
        timestamp = timestamp_match.group(1).replace('_', ':') if timestamp_match else None

        # Use first line as message, rest as notes
        lines = content.strip().split('\n')
        message = lines[0] if lines else "Untitled journal entry"
        notes = '\n'.join(lines[1:]) if len(lines) > 1 else ""

        tags, notes = extract_tags_notes(notes)

        fragments.append({
            "source_path": file_path,
            "timestamp": timestamp,
            "message": message,
            "tags": tags,
            "notes": notes,
            "status": "parsed"
        })

    except Exception as e:
        fragments.append({
            "source_path": file_path,
            "timestamp": None,
            "message": f"Error parsing journal: {str(e)}",
            "tags": [],
            "notes": "",
            "status": "error"
        })

    return fragments
