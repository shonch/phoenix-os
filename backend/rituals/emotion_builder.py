# phoenix_portfolio/backend/rituals/emotion_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from datetime import datetime

def build_emotion_request(payload: dict) -> FragmentLogRequest:
    """
    Build a PhoenixOS v1 FragmentLogRequest for the Emotion ritual.
    """

    title = payload.get("title")
    emotion = payload.get("emotion")
    body = payload.get("body")  # raw user text
    tags = (payload.get("tags") or []) + ["emotion"]

    return FragmentLogRequest(
        # Core identity
        module="emotion",
        layer="emotional",
        type="emotion",

        # Content
        title=title,
        subject=f"Emotion Logged: {emotion}" if emotion else None,
        raw_text=body,
        body=body,  # emotional grammar will rewrite this later

        # Tags
        tags=tags,
        resolved_tags=None,  # ingestion will fill this

        # Metadata
        source=payload.get("source", "ritual"),
        timestamp=payload.get("timestamp", datetime.utcnow()),
        mode=payload.get("mode"),
        metadata=payload.get("metadata", {}),
        extra={
            "emotion": emotion,
            "body": body,
        },

        # System
        version="phoenixos.v1",
    )

