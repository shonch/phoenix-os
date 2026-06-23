# phoenix_portfolio/backend/rituals/anti_grind_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from datetime import datetime

def build_anti_grind_request(payload: dict) -> FragmentLogRequest:
    """
    Build a PhoenixOS v1 FragmentLogRequest for the Anti-Grind ritual.
    """

    relief = payload.get("relief")
    cause = payload.get("cause")
    notes = payload.get("notes")  # raw user text
    tags = (payload.get("tags") or []) + ["anti_grind"]

    return FragmentLogRequest(
        # Core identity
        module="anti_grind",
        layer="emotional",
        type="anti_grind",

        # Content
        title=f"Anti-Grind Relief: {relief}" if relief else "Anti-Grind",
        subject=f"Cause: {cause}" if cause else None,
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
            "relief": relief,
            "cause": cause,
            "notes": notes,
        },

        # System
        version="phoenixos.v1",
    )

