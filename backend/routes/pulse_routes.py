# backend/routes/pulse_routes.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from backend.mongo_client import db
from backend.schemas.pulse import PulseFragmentCreate, PulseFragmentResponse
from backend.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/pulse", tags=["Pulse"])

# -------------------------
# CREATE
# -------------------------
@router.post("/", response_model=PulseFragmentResponse)
def log_pulse(entry: PulseFragmentCreate):
    doc = {
        "title": entry.title,
        "emotion": entry.emotion,
        "tags": entry.tags,
        "fragment": entry.fragment,
        "timestamp": datetime.utcnow(),
        "type": "pulse_fragment",
        "source": "pulse_routes",
    }
    result = db["emotional_fragments"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

# -------------------------
# READ (LIST)
# -------------------------
@router.get("/", response_model=list[PulseFragmentResponse])
def list_pulses():
    docs = list(db["emotional_fragments"].find({"type": "pulse_fragment"}))
    return serialize_docs(docs)

# -------------------------
# READ (SINGLE)
# -------------------------

@router.get("/{id}", response_model=PulseFragmentResponse)
def get_pulse(id: str):
    fragment = db["emotional_fragments"].find_one({"_id": ObjectId(id)})
    if not fragment:
        raise HTTPException(status_code=404, detail="Pulse fragment not found")
    return serialize_doc(fragment)
