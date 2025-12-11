# backend/routes/rituals/fragments_router.py
# Phoenix Fragments Router — Log Emotion ritual

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from backend.mongo_client import db
from backend.modules.symbolic_tag import create_tag, normalize_tag, suggest_tags

router = APIRouter(prefix="/rituals/fragments", tags=["fragments"])

class EmotionLog(BaseModel):
    subject: str
    tags: list[str]
    weather: str | None = None
    notes: str

@router.post("/log_emotion")
def log_emotion(entry: EmotionLog):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    final_tags = []

    # Normalize and suggest tags (for now, auto-pick normalized; GUI can expose suggestions later)
    for raw_tag in entry.tags:
        normalized = normalize_tag(raw_tag)
        suggestions = suggest_tags(normalized)
        if suggestions:
            final_tags.append(suggestions[0]["tag_name"])  # auto-pick first suggestion
        else:
            final_tags.append(normalized)

        # Ensure tag exists in symbolic_tags
        tag_data = {
            "tag_name": final_tags[-1],
            "title": final_tags[-1].replace("_", " ").title(),
            "emoji": "🌀",
            "archetype": "unclassified",
            "sass_level": 0,
            "emotional_weight": "neutral",
            "color": "#999999",
            "source_system": "phoenix",
            "description": "Auto-inserted from log_emotion endpoint",
            "dominatrix_affinity": [],
            "created_at": datetime.utcnow().isoformat()
        }
        create_tag(tag_data)

    # Markdown content
    md_content = f"""### 📜 Emotion Log

**Subject**: {entry.subject}  
**Tags**: {" ".join(final_tags)}  
**Weather**: {entry.weather}  
**Timestamp**: {timestamp}  

{entry.notes}
"""

    doc = {
        "subject": entry.subject,
        "tags": final_tags,
        "weather": entry.weather,
        "content": md_content,
        "date": timestamp,
        "source": "fragments_router"
    }
    result = db["fragments"].insert_one(doc)

    return {
        "message": "Emotion logged",
        "id": str(result.inserted_id),
        "tags": final_tags,
        "timestamp": timestamp
    }
