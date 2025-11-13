from utils import extract_tags_notes

def parse(content, file_path):
    fragments = []
    lines = content.strip().split('\n')

    # Use first line as message, rest as notes
    message = lines[0] if lines else "Untitled budget entry"
    notes = '\n'.join(lines[1:]) if len(lines) > 1 else ""

    tags, notes = extract_tags_notes(notes)

    fragments.append({
        "source_path": file_path,
        "message": message,
        "tags": tags,
        "notes": notes,
        "status": "parsed"
    })

    return fragments
