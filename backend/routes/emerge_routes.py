from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from backend.mongo_client import db
from backend.schemas.emerge import EmergeCreate, EmergeResponse
from backend.utils.serialization import serialize_doc, serialize_docs
from backend.modules.symbolic_tag import normalize_tag, create_tag

router = APIRouter(prefix="/emerge", tags=["Emerge"])

@router.post("/", response_model=EmergeResponse)
def log_revelation(entry: EmergeCreate):
    timestamp = datetime.utcnow()
    final_tags = [normalize_tag(tag) for tag in entry.tags] + ["emerge"]

    for tag in final_tags:
        create_tag({"tag_name": tag, "description": "Auto-inserted from emerge_routes"})

    md_content = f"""### 🌱 Unconscious Revelation

**Type**: {entry.rev_type}  
**Trigger**: {entry.trigger}  
**Weather**: {entry.weather or "N/A"}  
**Timestamp**: {timestamp.isoformat()}  

---

{entry.reflection or ""}
"""

    doc = {
        "subject": f"Revelation: {entry.rev_type}",
        "tags": final_tags,
        "weather": entry.weather,
        "content": md_content,
        "date": timestamp,
        "source": "emerge_routes",
    }
    result = db["revelations"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/", response_model=list[EmergeResponse])
def list_revelations():
    docs = list(db["revelations"].find())
    return serialize_docs(docs)

@router.get("/{id}", response_model=EmergeResponse)
def get_revelation(id: str):
    revelation = db["revelations"].find_one({"_id": ObjectId(id)})
    if not revelation:
        raise HTTPException(status_code=404, detail="Revelation not found")
    return serialize_doc(revelation)
