from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["phoenix_engine"]

def audit_tags():
    tag_index = db["tag_index"]
    symbolic_tags = db["symbolic_tags"]

    # Count untitled records
    untitled_index = tag_index.count_documents({ "title": { "$exists": False } })
    untitled_symbolic = symbolic_tags.count_documents({ "title": { "$exists": False } })

    # Sample records
    sample_index = list(tag_index.find().limit(5))
    sample_symbolic = list(symbolic_tags.find().limit(5))

    print("Untitled in tag_index:", untitled_index)
    print("Untitled in symbolic_tags:", untitled_symbolic)
    print("\nSample tag_index records:")
    for doc in sample_index:
        print(doc)
    print("\nSample symbolic_tags records:")
    for doc in sample_symbolic:
        print(doc)

if __name__ == "__main__":
    audit_tags()
