# search_phoenix.py — Phoenix MongoDB Search Ritual (Global Index Edition)
# Author: Shon Heersink & Copilot

from pymongo import MongoClient
import os
from dotenv import load_dotenv
import subprocess

def write_to_markdown(doc):
    title = doc.get("title") or doc.get("subject") or "Untitled Fragment"
    tags = ", ".join(doc.get("tags", [])) if isinstance(doc.get("tags"), list) else str(doc.get("tags"))
    date = doc.get("logged") or doc.get("timestamp") or doc.get("date") or "Unknown Date"
    content = doc.get("message") or doc.get("content") or "[No content found]"
    md_content = f"""# 🧠 {title}

**Tags**: {tags}  
**Date**: {date}  

---

{content}
"""

    filename = "phoenix_fragment.md"
    with open(filename, "w") as f:
        f.write(md_content)
    return filename

def view_with_glow(filename):
    subprocess.run(["glow", filename])

def run():
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")  # backend
    client = MongoClient(uri)
    db = client[db_name]

    query = input("🔍 Enter search term or tag: ").strip().lower()
    print(f"\n🧭 Searching all collections in '{db_name}' for: '{query}'\n")

    total_matches = 0
    all_matches = []

    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        try:
            for doc in collection.find():
                if any(query in str(value).lower() for value in doc.values()):
                    global_index = len(all_matches) + 1  # 1-based index
                    title = doc.get("title") or doc.get("subject") or "Untitled Fragment"
                    tags = ", ".join(doc.get("tags", [])) if isinstance(doc.get("tags"), list) else str(doc.get("tags"))
                    date = doc.get("logged") or doc.get("timestamp") or doc.get("date") or "Unknown Date"
                    content = doc.get("message") or doc.get("content") or "[No content found]"
                    snippet = content[:200].replace("\n", " ")

                    print(f"📂 {collection_name} — Match {global_index}")
                    print(f"### 🧠 Subject: {title}")
                    print(f"**Tags**: {tags}")
                    print(f"**Date**: {date}")
                    print(f"**Snippet**: {snippet}...\n")

                    all_matches.append(doc)
                    total_matches += 1
        except Exception as e:
            print(f"⚠️ Skipped {collection_name}: {e}")
            continue

    if total_matches == 0:
        print("🫧 No matches found. The fragment may still be forming.")
    else:
        print(f"\n✅ Total matches across Phoenix: {total_matches}")
        selection = input("✨ View full content of a match? Enter number or 'n' to skip: ").strip()
        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(all_matches):
                filename = write_to_markdown(all_matches[index])
                view_with_glow(filename)

if __name__ == "__main__":
    run()
