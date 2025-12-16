from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from backend.mongo_client import db
from backend.schemas.threshold_guard import ThresholdCreate, ThresholdResponse
from backend.utils.serialization import serialize_doc, serialize_docs
from backend.modules.symbolic_tag import normalize_tag, create_tag

router = APIRouter(prefix="/thresholds", tags=["Threshold Guard"])

@router.post("/", response_model=ThresholdResponse)
def log_threshold(entry: ThresholdCreate):
    timestamp = datetime.utcnow()
    emotional_weight = "heavy" if entry.status == "breached" else "neutral"
    final_tags = [normalize_tag(tag) for tag in entry.tags] + [normalize_tag(entry.anchor)]

    for tag in final_tags:
        tag_data = {
            "tag_name": tag,
            "emoji": "🌀",
            "archetype": "unclassified",
            "sass_level": 0,
            "emotional_weight": emotional_weight,
            "color": "#999999",
            "source_system": "phoenix",
            "description": "Auto-inserted from threshold_guard_routes",
            "dominatrix_affinity": []
        }
        create_tag(tag_data)

    md_content = f"""### 🛡️ Threshold Scan

**Type**: {entry.threshold_type}  
**Status**: {entry.status}  
**Anchor**: {entry.anchor}  
**Weather**: {entry.weather or "N/A"}  
**Timestamp**: {timestamp.isoformat()}  
"""

    doc = {
        "subject": f"Threshold: {entry.threshold_type}",
        "tags": final_tags,
        "weather": entry.weather,
        "content": md_content,
        "date": timestamp,
        "source": "threshold_guard_routes",
    }
    result = db["thresholds"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/", response_model=list[ThresholdResponse])
def list_thresholds():
    docs = list(db["thresholds"].find())
    return serialize_docs(docs)

@router.get("/{id}", response_model=ThresholdResponse)
def get_threshold(id: str):
    threshold = db["thresholds"].find_one({"_id": ObjectId(id)})
    if not threshold:
        raise HTTPException(status_code=404, detail="Threshold not found")
    return serialize_doc(threshold)
