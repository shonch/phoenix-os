# phoenix_portfolio/backend/engines/grind_engine.py

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc


Fragment = Dict[str, Any]


# ============================================================
#   GRIND ENGINE — counts and structural pattern detection only
# ============================================================

def analyze_grind_fragments(fragments: List[Fragment]) -> Dict[str, Any]:
    if not fragments:
        return {
            "patterns": [],
            "fatigue_indicators": [],
            "override_patterns": [],
            "cycles": [],
            "co_occurrence": {},
            "anomalies": [],
        }

    tag_counter = Counter()
    co_occurrence = defaultdict(Counter)
    scans: List[Fragment] = []
    overrides: List[Fragment] = []

    for frag in fragments:
        f_type = (frag.get("type") or "").lower()

        if f_type in ("grind_scan", "grind"):
            scans.append(frag)
        elif f_type in ("grind_override", "anti_grind"):
            overrides.append(frag)

        tags = _extract_tags(frag)
        for t in tags:
            tag_counter[t] += 1

        for i, t1 in enumerate(tags):
            for t2 in tags[i + 1:]:
                co_occurrence[t1][t2] += 1
                co_occurrence[t2][t1] += 1

    patterns = [
        {"tag": tag, "count": count}
        for tag, count in tag_counter.most_common(15)
    ]

    fatigue_indicators = _detect_fatigue(scans)
    override_patterns = _detect_overrides(overrides)
    cycles = _detect_cycles(scans, overrides)

    co_map = {
        tag: [{"tag": other, "count": c} for other, c in partners.most_common(10)]
        for tag, partners in co_occurrence.items()
    }

    anomalies = _detect_anomalies(scans, overrides)

    return {
        "patterns": patterns,
        "fatigue_indicators": fatigue_indicators,
        "override_patterns": override_patterns,
        "cycles": cycles,
        "co_occurrence": co_map,
        "anomalies": anomalies,
    }


# ============================================================
#   HELPERS (unchanged)
# ============================================================

def _extract_tags(frag: Fragment) -> List[str]:
    raw = frag.get("tags", [])
    tags: List[str] = []

    if isinstance(raw, dict):
        name = raw.get("tag_name") or raw.get("name")
        if name:
            tags.append(str(name))
    elif isinstance(raw, list):
        for t in raw:
            if isinstance(t, dict):
                name = t.get("tag_name") or t.get("name")
                if name:
                    tags.append(str(name))
            else:
                tags.append(str(t))
    elif isinstance(raw, str):
        tags.append(raw)

    return [t.lower() for t in tags if t]


def _parse_ts(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


def _extract_timestamp(frag: Fragment) -> Optional[datetime]:
    for key in ["timestamp", "date", "created_at", "inserted_at"]:
        ts = frag.get(key)
        if not ts:
            continue
        parsed = _parse_ts(ts)
        if parsed:
            return parsed
    return None


def _detect_fatigue(scans: List[Fragment]) -> List[Dict[str, Any]]:
    indicators = []

    for frag in scans:
        energy = frag.get("energy")
        sleep = frag.get("sleep")
        urgency = frag.get("urgency")

        if isinstance(energy, (int, float)) and energy <= 4:
            indicators.append({
                "id": frag.get("id"),
                "type": "low_energy",
                "energy": energy,
                "timestamp": frag.get("timestamp"),
            })

        if isinstance(sleep, str) and sleep.lower() == "poor":
            indicators.append({
                "id": frag.get("id"),
                "type": "poor_sleep",
                "timestamp": frag.get("timestamp"),
            })

        if isinstance(urgency, str) and urgency.lower() == "yes":
            indicators.append({
                "id": frag.get("id"),
                "type": "impulse_to_quit",
                "timestamp": frag.get("timestamp"),
            })

    return indicators


def _detect_overrides(overrides: List[Fragment]) -> List[Dict[str, Any]]:
    patterns = []

    for frag in overrides:
        action = frag.get("action")
        if action:
            patterns.append({
                "id": frag.get("id"),
                "action": action,
                "timestamp": frag.get("timestamp"),
            })

    return patterns


def _detect_cycles(scans: List[Fragment], overrides: List[Fragment]) -> List[Dict[str, Any]]:
    cycles: List[Dict[str, Any]] = []

    all_events = []
    for f in scans:
        ts = _extract_timestamp(f)
        if ts:
            all_events.append((ts, "scan", f))
    for f in overrides:
        ts = _extract_timestamp(f)
        if ts:
            all_events.append((ts, "override", f))

    all_events.sort(key=lambda x: x[0])

    for i in range(len(all_events) - 1):
        ts1, t1, f1 = all_events[i]
        ts2, t2, f2 = all_events[i + 1]

        if t1 == "scan" and t2 == "override":
            delta = ts2 - ts1
            cycles.append({
                "scan_id": f1.get("id"),
                "override_id": f2.get("id"),
                "time_between": delta.total_seconds() / 60,
                "timestamp_scan": f1.get("timestamp"),
                "timestamp_override": f2.get("timestamp"),
            })

    return cycles


def _detect_anomalies(scans: List[Fragment], overrides: List[Fragment]) -> List[Dict[str, Any]]:
    anomalies: List[Dict[str, Any]] = []

    if len(scans) == 1:
        anomalies.append({"type": "single_scan", "id": scans[0].get("id")})

    if len(overrides) == 1:
        anomalies.append({"type": "single_override", "id": overrides[0].get("id")})

    return anomalies


def analyze_grind(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for analyze_grind_fragments.
    Loads grind/anti_grind fragments from emotional_fragments (the current
    ritual pipeline's collection), plus legacy grind_scan/grind_override
    fragments from the old 'fragments' collection, so both old and new
    data are visible.
    """
    current_docs = [
        serialize_doc(d)
        for d in db["emotional_fragments"]
        .find({"user_id": user_id, "type": {"$in": ["grind", "anti_grind"]}})
        .sort("timestamp", -1)
    ]

    legacy_docs = [
        serialize_doc(d)
        for d in db["fragments"]
        .find({"user_id": user_id, "type": {"$in": ["grind_scan", "grind_override"]}})
        .sort("timestamp", -1)
    ]

    return analyze_grind_fragments(current_docs + legacy_docs)
