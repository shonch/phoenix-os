from utils import extract_tags_notes

def parse(content, file_path):
    fragments = []
    lines = content.strip().split('\n')

    # Use first non-empty line as message
    message = next((line for line in lines if line.strip()), "Untitled ritual concept")
    notes = '\n'.join(lines)

    tags, notes = extract_tags_notes(notes)

    fragments.append({
        "source_path": file_path,
        "message": message,
        "tags": tags,
        "notes": notes,
        "status": "parsed"
    })

    return fragments
