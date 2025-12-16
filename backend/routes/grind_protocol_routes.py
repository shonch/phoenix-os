from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from backend.mongo_client import db
from backend.schemas.grind_protocol import GrindScanCreate, GrindScanResponse
from backend.utils.serialization import serialize_doc, serialize_docs
from backend.modules.symbolic_tag import normalize_tag, create_tag

router = APIRouter(prefix="/grind", tags=["Grind Protocol"])

@router.post("/", response_model=GrindScanResponse)
def log_scan(entry: GrindScanCreate):
    timestamp = datetime.utcnow()
    status = entry.status or ("pause" if entry.energy <= 4 or entry.sleep == "poor" or entry.urgency == "yes" else "clear")
    final_tags = [normalize_tag(tag) for tag in entry.tags] + ["grind_scan"]

    for tag in final_tags:
        create_tag({"tag_name": tag, "description": "Auto-inserted from grind_protocol_routes"})

    md_content = f"""### ⚠️ Grind Protocol Scan
**Energy Level**: {entry.energy}  
**Sleep Quality**: {entry.sleep}  
**Emotional State**: {entry.state}  
**Urgency to Quit**: {entry.urgency}  
**Status**: {status}  
**Timestamp**: {timestamp.isoformat()}  
"""

    doc = {
        "energy": entry.energy,
        "sleep": entry.sleep,
        "state": entry.state,
        "urgency": entry.urgency,
        "status": status,
        "tags": final_tags,
        "timestamp": timestamp,
        "type": "grind_scan",
        "content": md_content,
        "note": "Grind protocol scan completed.",
        "source_system": "grind_protocol_routes",
    }
    result = db["emotional_fragments"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/", response_model=list[GrindScanResponse])
def list_scans():
    docs = list(db["emotional_fragments"].find({"type": "grind_scan"}))
    return serialize_docs(docs)

@router.get("/{id}", response_model=GrindScanResponse)
def get_scan(id: str):
    scan = db["emotional_fragments"].find_one({"_id": ObjectId(id)})
    if not scan:
        raise HTTPException(status_code=404, detail="Grind scan not found")
    return serialize_doc(scan)
