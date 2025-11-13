import re

def extract_tags_notes(text):
    """
    Extracts tags from a line like 'Tags: grief, awe, restoration'
    Returns (tags_list, cleaned_text)
    """
    tags = []
    lines = text.strip().split('\n')
    cleaned_lines = []

    for line in lines:
        if line.lower().startswith("tag:") or line.lower().startswith("tags:"):
            tag_line = line.split(":", 1)[1]
            tags = [tag.strip() for tag in tag_line.split(",") if tag.strip()]
        else:
            cleaned_lines.append(line)

    cleaned_text = '\n'.join(cleaned_lines).strip()
    return tags, cleaned_text
