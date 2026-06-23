# phoenix_portfolio/backend/rituals/pulse_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from datetime import datetime

def build_pulse_request(payload: dict) -> FragmentLogRequest:
    """
    Build a PhoenixOS v1 FragmentLogRequest for the Pulse ritual.
    """

    title = payload.get("title")
    emotion = payload.get("emotion")
    fragment = payload.get("raw_fragment")  # raw user text
    tags = (payload.get("tags") or []) + ["pulse"]

    return FragmentLogRequest(
        # Core identity
        module="pulse",
        layer="emotional",
        type="pulse",

        # Content
        title=title,
        subject=f"Emotion: {emotion}" if emotion else None,
        raw_text=fragment,
        body=fragment,  # emotional_grammar will rewrite this later

        # Tags
        tags=tags,  # list of tag IDs (strings)
        resolved_tags=None,  # ingestion will fill this

        # Metadata
        source=payload.get("source", "ritual"),
        timestamp=payload.get("timestamp", datetime.utcnow()),
        mode=payload.get("mode"),
        metadata=payload.get("metadata", {}),
        extra={
            "emotion": emotion,
            "raw_fragment": fragment,
            "title": title,
        },

        # System
        version="phoenixos.v1",
    )

