# phoenix_portfolio/backend/engines/threshold_emerge_engine.py

from datetime import datetime
from typing import Any, Dict, List

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.adapter import (
    NormalizedFragment,
    normalize_fragment,
)


def _load_thresholds(user_id: str) -> List[NormalizedFragment]:
    docs = list(db["thresholds"].find({"user_id": user_id}))
    return [normalize_fragment(d, "thresholds") for d in docs]


def analyze_thresholds(user_id: str) -> Dict[str, Any]:
    th = _load_thresholds(user_id)

    fatigue: List[NormalizedFragment] = []
    for f in th:
        text_bits = [
            f.subject or "",
            f.content or "",
            " ".join(f.tags or []),
        ]
        joined = " ".join(text_bits).lower()
        if "fatigue" in joined:
            fatigue.append(f)

    fatigue_sorted = sorted(
        fatigue,
        key=lambda x: x.timestamp or datetime.min,
        reverse=True,
    )

    return {
        "total_thresholds": len(th),
        "fatigue_events": len(fatigue),
        "recent_fatigue": [
            {
                "id": getattr(f, "id", None),
                "subject": f.subject,
                "weather": f.weather,
                "date": f.date_raw,
            }
            for f in fatigue_sorted[:5]
        ],
    }
