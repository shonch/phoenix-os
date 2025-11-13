# inspect_collections.py — PhoenixOS Fragment Interpreter (Canon Edition)
# Author: Shon Heersink & Copilot

import os
from datetime import datetime
from dotenv import load_dotenv
from backend.mongo_client import db

def interpret_fragment(doc):
    tags = doc.get("tags", [])
    tone = "neutral"
    if "grief" in tags: tone = "grief"
    elif "awe" in tags: tone = "awe"
    elif "ritual_trigger" in tags: tone = "ritual"
    elif "frisson" in tags: tone = "frisson"
    elif "resonance" in tags: tone = "resonance"
    unresolved = not tags or "unresolved" in tags
    return {"tone": tone, "unresolved": unresolved, "tags": tags}

def format_fragment(doc, collection):
    interp = interpret_fragment(doc)
    title = f"Phoenix Fragment {str(doc.get('_id'))[:6]}"
    body = doc.get("message", "🕳️ Empty vessel")
    tags = ", ".join(interp["tags"]) if interp["tags"] else "🌫️ No tags found"
    interpretation = doc.get("interpretation", "")
    tone = interp["tone"]
    unresolved = "⚠️ Unresolved" if interp["unresolved"] else "✅ Resolved"

    # Interpret notes
    notes = doc.get("notes", "")
    lines = notes.splitlines()
    recovered_paths = []
    skipped_paths = []
    other_notes = []

    for line in lines:
        if line.startswith("❓ Unknown format skipped:"):
            skipped_path = line.replace("❓ Unknown format skipped:", "").strip()
            normalized_path = os.path.abspath(skipped_path)
            recovered = collection.find_one({"source_path": normalized_path, "fragment": "recovered"})
            if recovered:
                recovered_paths.append(normalized_path)
            else:
                skipped_paths.append(normalized_path)
        else:
            other_notes.append(line)

    notes = ""
    if recovered_paths:
        notes += "🛡️ Recovered fragments:\n" + "\n".join(f"- {p}" for p in recovered_paths) + "\n"
    if skipped_paths:
        notes += "⚠️ Still skipped:\n" + "\n".join(f"- {p}" for p in skipped_paths) + "\n"
    if other_notes:
        notes += "\n".join(other_notes)

    return f"""
📝 **{title}**
{body}

🧾 Notes:
{notes}
🔮 Interpretation: {interpretation}
🎭 Tone: {tone}
🏷️ Tags: {tags}
{unresolved}
"""

def run():
    load_dotenv()
    print("\n📂 Collections in backend:")
    collections = db.list_collection_names()
    for name in collections:
        print(f" - {name}")

    name = input("\nEnter collection name to inspect: ")
    if name not in collections:
        print(f"⚠️ Collection '{name}' not found.")
        return

    sort = input("Sort by field (optional): ")
    collection = db[name]
    query = {}
    sort_order = [(sort, -1)] if sort else None
    docs = collection.find(query).sort(sort_order) if sort_order else collection.find(query)

    print(f"\n🔍 Interpreted Fragments in '{name}':")
    doc_list = []
    for i, doc in enumerate(docs, start=1):
        interp = interpret_fragment(doc)
        frag_id = str(doc.get("_id"))[:6]
        tags = ", ".join(interp["tags"]) if interp["tags"] else "🌫️ No tags found"
        unresolved = "⚠️ Unresolved" if interp["unresolved"] else "✅ Resolved"
        print(f"{i}. Phoenix Fragment {frag_id} — {tags} — {unresolved}")
        doc_list.append(doc)

    choice = input("\nEnter fragment number to view full Markdown (or press Enter to skip): ").strip()
    print(f"🧪 Raw input captured: '{choice}'")
    if choice.isdigit():
        print("🧪 Entered digit block")
        index = int(choice) - 1
        if 0 <= index < len(doc_list):

            doc = doc_list[index]
            # Preview header using actual fields
            print(f"🧪 doc keys: {list(doc.keys())}")
            print(f"🧪 doc type: {type(doc)}")
            preview_title = doc.get("title") or "Untitled Fragment"
            preview_tags = ", ".join(doc.get("tags", [])) or "🌫️ No tags found"
            preview_date = doc.get("logged") or doc.get("timestamp") or "Unknown Date"

            print(f"\n   🧠 {preview_title}")
            print(f"  Tags: {preview_tags}")
            print(f"  Date: {preview_date}")
            print("\n  --------\n")

            #print(format_fragment(doc, collection))
        else:
            print("⚠️ Invalid selection.")
    else:
        print("🔚 No fragment selected. Returning to Phoenix console.")
