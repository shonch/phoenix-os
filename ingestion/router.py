def route_file(md_path):
    if "frisson_journal/entries" in md_path:
        from formats import journal
        return journal.parse(md_path)
    # Add more formats here
    else:
        return [{
            "source_path": md_path,
            "message": "Unrecognized format",
            "tags": [],
            "notes": "",
            "status": "unknown"
        }]
