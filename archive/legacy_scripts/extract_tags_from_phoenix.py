# extract_tags_from_phoenix.py — Extract symbolic tags from Phoenix and index them

import os
from pymongo import MongoClient
from dotenv import dotenv_values
import re

# Load Phoenix .env
phoenix_env = os.path.abspath(".env")
env_vars = dotenv_values(phoenix_env)
uri = env_vars.get("MONGO_URI")
db_name = env_vars.get("DB_NAME")

client = MongoClient(uri)
db = client[db_name]
tag_index = db["tag_index"]

# Collections to scan
collections = ["emotional_fragments", "clues", "revelations", "fragments"]

# Regex patterns for symbolic tags
tag_patterns = [
    r"\[tag:\s*(.*?)\]",         # [tag: resonance]
    r"tags:\s*\[(.*?)\]",        # tags: [mythic, fragment]
    r"#\s*(\w+)",                # #grief
    r"##\s*(\w+)",               # ##protector
    r"\*\*Symbol\*\*:\s*(.*?)\s",# **Symbol**: fragment glow
    r"🌀\s*\w+",                 # 🌀 Transition
    r"🧮\s*\w+",                 # 🧮 Algorithmic Grip
]

def extract_tags(text):
    tags = set()
    for pattern in tag_patterns:
        matches = re.findall(pattern, text or "")
        for match in matches:
            if isinstance(match, str):
                for tag in match.split(","):
                    tags.add(tag.strip())
    return list(tags)

def process_collection(name):
    print(f"\n🔍 Scanning {name}...")
    for doc in db[name].find():
        doc_id = str(doc["_id"])
        fields = ["tags", "content", "message", "note", "notes"]
        found_tags = set()

        for field in fields:
            value = doc.get(field)
            if isinstance(value, list):
                found_tags.update([t.strip() for t in value])
            elif isinstance(value, str):
                found_tags.update(extract_tags(value))

        for tag in found_tags:
            if tag:
                tag_doc = {
                    "label": tag,
                    "type": "symbolic_tag",
                    "source_collection": name,
                    "document_id": doc_id,
                    "context": doc.get("content") or doc.get("message") or doc.get("note") or doc.get("notes", ""),
                }
                tag_index.insert_one(tag_doc)
                print(f"✅ Indexed tag: {tag} from {name} ({doc_id})")

process_collection("emotional_fragments")
process_collection("clues")
process_collection("revelations")
process_collection("fragments")
