def parse(content, source_path):
    with open("log.md", "a") as log_file:
        log_file.write(f"- ⏳ Tracker format deferred: {source_path}\n")
    return []
