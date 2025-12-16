from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from backend.mongo_client import db
from backend.schemas.anti_grind import AntiGrindCreate, AntiGrindResponse
from backend.utils.serialization import serialize_doc, serialize_docs
from backend.modules.symbolic_tag import normalize_tag, create_tag

router = APIRouter(prefix="/anti_grind", tags=["Anti-Grind"])

@router.post("/", response_model=AntiGrindResponse)
def log_override(entry: AntiGrindCreate):
    timestamp = datetime.utcnow()
    final_tags = [normalize_tag(tag) for tag in entry.tags] + ["grind_override"]

    for tag in final_tags:
        create_tag({"tag_name": tag, "description": "Auto-inserted from anti_grind_routes"})

    md_content = f"""### ⛔ Anti-Grind Override
**Signal**: {entry.signal}  
**Action**: {entry.action}  
**Weather**: {entry.weather or "N/A"}  
**Timestamp**: {timestamp.isoformat()}  
"""

    doc = {
        "signal": entry.signal,
        "action": entry.action,
        "weather": entry.weather,
        "tags": final_tags,
        "timestamp": timestamp,
        "type": "grind_override",
        "content": md_content,
        "note": "Grind override protocol activated.",
        "source_system": "anti_grind_routes",
    }
    result = db["emotional_fragments"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/", response_model=list[AntiGrindResponse])
def list_overrides():
    docs = list(db["emotional_fragments"].find({"type": "grind_override"}))
    return serialize_docs(docs)

@router.get("/{id}", response_model=AntiGrindResponse)
def get_override(id: str):
    override = db["emotional_fragments"].find_one({"_id": ObjectId(id)})
    if not override:
        raise HTTPException(status_code=404, detail="Override not found")
    return serialize_doc(override)
