def log(content, source_path):
    with open("log.md", "a") as log_file:
        log_file.write(f"- ❓ Unknown format skipped: {source_path}\n")
    return []
