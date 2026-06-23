# phoenix_portfolio/backend/rituals/detective_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from datetime import datetime

def build_detective_request(payload: dict) -> FragmentLogRequest:
    """
    Build a PhoenixOS v1 FragmentLogRequest for the Detective ritual.
    """

    clue = payload.get("clue")
    insight = payload.get("insight")  # raw user text
    tags = (payload.get("tags") or []) + ["detective"]

    return FragmentLogRequest(
        # Core identity
        module="detective",
        layer="revelation",
        type="detective",

        # Content
        title=f"Detective Clue: {clue}" if clue else "Detective Clue",
        subject="Revelation Insight",
        raw_text=insight,
        body=insight,  # emotional grammar will rewrite this later

        # Tags
        tags=tags,
        resolved_tags=None,  # ingestion will fill this

        # Metadata
        source=payload.get("source", "ritual"),
        timestamp=payload.get("timestamp", datetime.utcnow()),
        mode=payload.get("mode"),
        metadata=payload.get("metadata", {}),
        extra={
            "clue": clue,
            "insight": insight,
        },

        # System
        version="phoenixos.v1",
    )

