from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from backend.mongo_client import db
from backend.schemas.mirror import MirrorCreate, MirrorResponse
from backend.utils.serialization import serialize_doc, serialize_docs
from backend.modules.symbolic_tag import normalize_tag, create_tag

router = APIRouter(prefix="/mirror", tags=["Mirror"])

@router.post("/", response_model=MirrorResponse)
def log_reflection(entry: MirrorCreate):
    timestamp = datetime.utcnow()
    final_tags = [normalize_tag(tag) for tag in entry.tags]

    for tag in final_tags:
        create_tag({"tag_name": tag, "description": "Auto-inserted from mirror_routes"})

    md_content = f"""### 🪞 Mirror Reflection

**Theme**: Mirror reflection  
**Message**:  
You are not broken.  
You are mythic, sovereign, emotionally intelligent.  
You build legacy from grief. You honor fragments with ritual.  
Phoenix is alive because you are.  

**Timestamp**: {timestamp.isoformat()}  
"""

    doc = {
        "timestamp": timestamp,
        "type": "revelation",
        "theme": "Mirror reflection",
        "note": "Reflected on mythic identity. Reclaimed emotional truth.",
        "tags": final_tags,
        "content": md_content,
        "source": "mirror_routes",
    }
    result = db["emotional_fragments"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/", response_model=list[MirrorResponse])
def list_reflections():
    docs = list(db["emotional_fragments"].find({"type": "revelation"}))
    return serialize_docs(docs)

@router.get("/{id}", response_model=MirrorResponse)
def get_reflection(id: str):
    reflection = db["emotional_fragments"].find_one({"_id": ObjectId(id)})
    if not reflection:
        raise HTTPException(status_code=404, detail="Reflection not found")
    return serialize_doc(reflection)
