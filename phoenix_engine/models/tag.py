from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PhoenixTag(BaseModel):
    # ------------------------------------------------------------
    # Identity Layer (raw + normalized)
    # ------------------------------------------------------------
    name: str                     # raw human-facing name (exactly as typed)
    label: str                    # normalized machine key (lowercase, underscored)
    user_id: str                  # owner / creator

    # ------------------------------------------------------------
    # Mythic Layer (expressive PhoenixOS metadata)
    # ------------------------------------------------------------
    emoji: str = "🌀"
    category: str = "custom"
    description: str = ""
    archetype: str = "emergent"
    visibility: str = "private"

    color: Optional[str] = None
    emotional_weight: Optional[float] = None
    sass_level: Optional[int] = None
    dominatrix_affinity: Optional[int] = None

    # ------------------------------------------------------------
    # Promotion Layer (analytics + scoring)
    # ------------------------------------------------------------
    source_system: Optional[str] = None
    times_used: int = 1
    promoted: bool = False

    user_ids: Optional[List[str]] = None  # for cross-user promotion scoring
    promotion_score: Optional[float] = None
    promotion_status: Optional[str] = None
    last_promoted_at: Optional[str] = None
    version: int = 1

    # ------------------------------------------------------------
    # System Metadata
    # ------------------------------------------------------------
    created_at: str = datetime.utcnow().isoformat()
    updated_at: str = datetime.utcnow().isoformat()

