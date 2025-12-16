# backend/utils/serialization.py
from bson import ObjectId

def serialize_doc(doc):
    """
    Convert MongoDB document to a JSON-friendly dict.
    - Renames _id to id (string)
    - Leaves other fields intact
    """
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

def serialize_docs(docs):
    """
    Convert a list of MongoDB documents.
    """
    return [serialize_doc(d) for d in docs if d]
