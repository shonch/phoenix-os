# phoenix_portfolio/backend/rituals/mirror_builder.py

from phoenix_portfolio.backend.schemas.api_fragments import FragmentLogRequest
from datetime import datetime

def build_mirror_request(payload: dict) -> FragmentLogRequest:
    """
    Build a PhoenixOS v1 FragmentLogRequest for the Mirror ritual.
    """

    reflection = payload.get("reflection")  # raw user text
    distortion = payload.get("distortion")
    tags = (payload.get("tags") or []) + ["mirror"]

    return FragmentLogRequest(
        # Core identity
        module="mirror",
        layer="revelation",
        type="mirror",

        # Content
        title="Mirror Reflection",
        subject=f"Distortion: {distortion}" if distortion else None,
        raw_text=reflection,
        body=reflection,  # emotional grammar will rewrite this later

        # Tags
        tags=tags,
        resolved_tags=None,  # ingestion will fill this

        # Metadata
        source=payload.get("source", "ritual"),
        timestamp=payload.get("timestamp", datetime.utcnow()),
        mode=payload.get("mode"),
        metadata=payload.get("metadata", {}),
        extra={
            "reflection": reflection,
            "distortion": distortion,
        },

        # System
        version="phoenixos.v1",
    )

