import os
from handlers import changelog, tracker, journal, unknown

def detect_format(content, file_path):
    if "## ENTRY START" in content and "## ENTRY END" in content:
        return "changelog"
    elif "| Stream" in content or "| Week of" in content:
        return "tracker"
    elif "**20" in content and "Tag:" in content:
        return "journal"
    elif "purchase" in content or "budget" in file_path:
        return "budget"
    elif "ritual" in file_path or "sacred" in content:
        return "ritual"
    elif "schema" in file_path or "sketch" in file_path:
        return "schema"
    elif "def " in content or "import " in content or "code" in file_path:
        return "code"
    elif "purchase" in content or "budget" in file_path:
        return "budget"
 
    elif "README" in file_path or "index.md" in file_path:
        return "meta"
    else:
        return "unknown"

def route_file(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    format_type = detect_format(content, md_path)
    print(f"Detected format: {format_type} → {md_path}")

    if format_type == "changelog":
        return changelog.parse(content, md_path)
    elif format_type == "tracker":
        return tracker.parse(content, md_path)
    elif format_type == "journal":
        return journal.parse(content, md_path)
    elif "frisson_journal/entries" in md_path:
        from formats import journal
        return journal.parse(md_path)
    elif format_type == "ritual":
        from handlers import ritual
        return ritual.parse(content, md_path)
    elif format_type == "budget":
        from handlers import budget
        return budget.parse(content, md_path)
    elif format_type == "schema":
        from handlers import schema
        return schema.parse(content, md_path)
    elif format_type == "code":
        from handlers import code
        return code.parse(content, md_path)
    elif format_type == "meta":
        from handlers import meta
        return meta.parse(content, md_path)
    else:
        return unknown.log(content, md_path)

def scan_manifest(manifest_path):
    parsed_fragments = []
    with open(manifest_path, 'r') as f:
        paths = [line.strip() for line in f if line.strip()]

    for md_path in paths:
        if os.path.exists(md_path) and md_path.endswith(".md"):
            fragments = route_file(md_path)
            parsed_fragments.extend(fragments)
        else:
            print(f"⚠️ Skipped: {md_path} (missing or invalid)")
            with open("log.md", "a") as log_file:
                log_file.write(f"- ⚠️ Missing or invalid path: {md_path}\n")
    return parsed_fragments

if __name__ == "__main__":
    manifest = "../../md_manifest.txt"  # Adjust if needed
    all_fragments = scan_manifest(manifest)
    print(f"Total fragments parsed: {len(all_fragments)}")
# Example usage
if __name__ == "__main__":
    manifest = "../../md_manifest.txt"  # Adjust path if needed
    all_fragments = scan_manifest(manifest)
    print(f"Total fragments parsed: {len(all_fragments)}")
