# phoenix_portfolio/backend/rituals/grind_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from datetime import datetime

def build_grind_request(payload: dict) -> FragmentLogRequest:
    """
    Build a PhoenixOS v1 FragmentLogRequest for the Grind ritual.
    """

    task = payload.get("task")
    resistance = payload.get("resistance")
    notes = payload.get("notes")  # raw user text
    tags = (payload.get("tags") or []) + ["grind"]

    return FragmentLogRequest(
        # Core identity
        module="grind",
        layer="emotional",
        type="grind",

        # Content
        title=f"Grind Protocol: {task}" if task else "Grind Protocol",
        subject=f"Resistance: {resistance}" if resistance else None,
        raw_text=notes,
        body=notes,  # emotional grammar will rewrite this later

        # Tags
        tags=tags,
        resolved_tags=None,  # ingestion will fill this

        # Metadata
        source=payload.get("source", "ritual"),
        timestamp=payload.get("timestamp", datetime.utcnow()),
        mode=payload.get("mode"),
        metadata=payload.get("metadata", {}),
        extra={
            "task": task,
            "resistance": resistance,
            "notes": notes,
        },

        # System
        version="phoenixos.v1",
    )

