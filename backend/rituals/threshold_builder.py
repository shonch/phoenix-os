# phoenix_portfolio/backend/rituals/threshold_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from datetime import datetime

def build_threshold_request(payload: dict) -> FragmentLogRequest:
    """
    Build a PhoenixOS v1 FragmentLogRequest for the Threshold ritual.
    """

    boundary = payload.get("boundary")
    violation = payload.get("violation")  # raw user text
    tags = (payload.get("tags") or []) + ["threshold"]

    return FragmentLogRequest(
        # Core identity
        module="threshold",
        layer="threshold",
        type="threshold",

        # Content
        title=f"Threshold: {boundary}" if boundary else "Threshold",
        subject=f"Violation: {violation}" if violation else None,
        raw_text=violation,
        body=violation,  # emotional grammar will rewrite this later

        # Tags
        tags=tags,
        resolved_tags=None,  # ingestion will fill this

        # Metadata
        source=payload.get("source", "ritual"),
        timestamp=payload.get("timestamp", datetime.utcnow()),
        mode=payload.get("mode"),
        metadata=payload.get("metadata", {}),
        extra={
            "boundary": boundary,
            "violation": violation,
        },

        # System
        version="phoenixos.v1",
    )

