# phoenix_portfolio/backend/utils/adapter.py

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from phoenix_portfolio.backend.utils.serialization import serialize_doc


class NormalizedFragment(BaseModel):
    id: str
    collection: str

    subject: Optional[str] = None
    content: Optional[str] = None
    tags: List[str] = []
    weather: Optional[str] = None

    timestamp: Optional[datetime] = None
    date_raw: Optional[str] = None

    type: Optional[str] = None
    theme: Optional[str] = None
    note: Optional[str] = None
    source: Optional[str] = None

    raw: Dict[str, Any]


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value

    s = str(value)
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def normalize_fragment(doc: Dict[str, Any], collection: str) -> NormalizedFragment:
    raw = serialize_doc(doc) if "_id" in doc else doc
    _id = str(raw.get("_id"))

    subject = raw.get("subject") or raw.get("message")
    content = raw.get("content") or raw.get("notes")

    tags = raw.get("tags") or []
    if tags is None:
        tags = []
    if not isinstance(tags, list):
        tags = [str(tags)]
    tags = [str(t) for t in tags]

    weather = raw.get("weather")

    ts = raw.get("timestamp") or raw.get("inserted_at") or raw.get("date")
    parsed_ts = _parse_timestamp(ts)
    date_raw = str(ts) if ts is not None else None

    ftype = raw.get("type")
    theme = raw.get("theme")
    note = raw.get("note") or raw.get("notes")
    source = raw.get("source") or raw.get("source_path")

    return NormalizedFragment(
        id=_id,
        collection=collection,
        subject=subject,
        content=content,
        tags=tags,
        weather=weather,
        timestamp=parsed_ts,
        date_raw=date_raw,
        type=ftype,
        theme=theme,
        note=note,
        source=source,
        raw=raw,
    )

