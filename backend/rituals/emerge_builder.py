# phoenix_portfolio/backend/rituals/emerge_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from datetime import datetime

def build_emerge_request(payload: dict) -> FragmentLogRequest:
    """
    Build a PhoenixOS v1 FragmentLogRequest for the Emerge ritual.
    """

    breakthrough = payload.get("breakthrough")
    context = payload.get("context")  # raw user text
    tags = (payload.get("tags") or []) + ["emerge"]

    return FragmentLogRequest(
        # Core identity
        module="emerge",
        layer="revelation",
        type="emerge",

        # Content
        title="Emergence",
        subject=f"Breakthrough: {breakthrough}" if breakthrough else None,
        raw_text=context,
        body=context,  # emotional grammar will rewrite this later

        # Tags
        tags=tags,
        resolved_tags=None,  # ingestion will fill this

        # Metadata
        source=payload.get("source", "ritual"),
        timestamp=payload.get("timestamp", datetime.utcnow()),
        mode=payload.get("mode"),
        metadata=payload.get("metadata", {}),
        extra={
            "breakthrough": breakthrough,
            "context": context,
        },

        # System
        version="phoenixos.v1",
    )

