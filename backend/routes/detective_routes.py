from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from backend.mongo_client import db
from backend.schemas.detective import DetectiveCreate, DetectiveResponse
from backend.utils.serialization import serialize_doc, serialize_docs
from backend.modules.symbolic_tag import normalize_tag, create_tag

router = APIRouter(prefix="/detective", tags=["Detective"])

@router.post("/", response_model=DetectiveResponse)
def log_clue(entry: DetectiveCreate):
    timestamp = datetime.utcnow()
    final_tags = [normalize_tag(tag) for tag in entry.tags]

    for tag in final_tags:
        create_tag({"tag_name": tag, "description": "Auto-inserted from detective_routes"})

    md_content = f"""### 🕵️ Detective Log
**Clue**: {entry.clue}  
**Source**: {entry.source}  
**Timestamp**: {timestamp.isoformat()}  
"""

    doc = {
        "clue": entry.clue,
        "source": entry.source,
        "tags": final_tags,
        "timestamp": timestamp,
        "type": "detective_clue",
        "content": md_content,
        "note": "Detective clue logged.",
        "source_system": "detective_routes",
    }
    result = db["emotional_fragments"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/", response_model=list[DetectiveResponse])
def list_clues():
    docs = list(db["emotional_fragments"].find({"type": "detective_clue"}))
    return serialize_docs(docs)

@router.get("/{id}", response_model=DetectiveResponse)
def get_clue(id: str):
    clue = db["emotional_fragments"].find_one({"_id": ObjectId(id)})
    if not clue:
        raise HTTPException(status_code=404, detail="Clue not found")
    return serialize_doc(clue)
