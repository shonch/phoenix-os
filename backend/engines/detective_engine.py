# phoenix_portfolio/backend/engines/detective_engine.py

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter, defaultdict

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.adapter import (
    NormalizedFragment,
    normalize_fragment,
)


# ---------- Data loading ----------

def _load_clues(user_id: str) -> List[NormalizedFragment]:
    docs = list(db["clues"].find({"user_id": user_id}))
    return [normalize_fragment(d, "clues") for d in docs]


def _load_revelations(user_id: str) -> List[NormalizedFragment]:
    docs = list(db["revelations"].find({"user_id": user_id}))
    return [normalize_fragment(d, "revelations") for d in docs]


# ---------- Parsing helpers ----------

def _extract_type_from_subject(subject: Optional[str], prefix: str) -> Optional[str]:
    if not subject:
        return None
    if ":" in subject:
        left, right = subject.split(":", 1)
        if left.strip().lower() == prefix.lower():
            return right.strip().lower()
    return None


def _status_from_subject(subject: Optional[str]) -> str:
    if not subject:
        return "unknown"
    s = subject.lower()
    if "unresolved" in s:
        return "unresolved"
    if "integrated" in s:
        return "integrated"
    if "echo" in s or "echoing" in s:
        return "echoing"
    return "unknown"


def _recent(fs: List[NormalizedFragment], limit: int = 5) -> List[Dict[str, Any]]:
    return [
        {
            "id": getattr(f, "id", None),
            "subject": f.subject,
            "date": f.date_raw,
            "weather": f.weather,
        }
        for f in sorted(
            fs, key=lambda x: x.timestamp or datetime.min, reverse=True
        )[:limit]
    ]


# ---------- Symbolic + echo analysis ----------

def _analyze_symbols(clues: List[NormalizedFragment]) -> Dict[str, Any]:
    tag_counts: Counter[str] = Counter()
    pair_counts: Counter[Tuple[str, str]] = Counter()
    archetype_counts: Counter[str] = Counter()

    for f in clues:
        tag_names = []
        for t in (f.tags or []):
            name = getattr(t, "name", None) or getattr(t, "label", None) or t.get("name") if isinstance(t, dict) else None
            if name:
                tag_names.append(name)

            archetype = getattr(t, "archetype", None) or (t.get("archetype") if isinstance(t, dict) else None)
            if archetype:
                archetype_counts[archetype] += 1

        tag_counts.update(tag_names)

        unique_tags = sorted(set(tag_names))
        for i in range(len(unique_tags)):
            for j in range(i + 1, len(unique_tags)):
                pair_counts[(unique_tags[i], unique_tags[j])] += 1

    top_tags = [
        {"tag": tag, "count": count}
        for tag, count in tag_counts.most_common(10)
    ]

    top_pairs = [
        {"tags": [a, b], "count": count}
        for (a, b), count in pair_counts.most_common(10)
    ]

    top_archetypes = [
        {"archetype": a, "count": c}
        for a, c in archetype_counts.most_common(10)
    ]

    symbolic_density = len(tag_counts)

    return {
        "top_tags": top_tags,
        "top_pairs": top_pairs,
        "top_archetypes": top_archetypes,
        "symbolic_density": symbolic_density,
    }


def _analyze_weather(clues: List[NormalizedFragment]) -> Dict[str, Any]:
    weather_counts: Counter[str] = Counter()
    for f in clues:
        if f.weather:
            weather_counts[f.weather] += 1

    distribution = [
        {"weather": w, "count": c}
        for w, c in weather_counts.most_common()
    ]

    recent_weather = [
        {
            "subject": f.subject,
            "weather": f.weather,
            "date": f.date_raw,
        }
        for f in sorted(
            [c for c in clues if c.weather],
            key=lambda x: x.timestamp or datetime.min,
            reverse=True,
        )[:10]
    ]

    return {
        "distribution": distribution,
        "recent": recent_weather,
    }


def _detect_echoes(clues: List[NormalizedFragment]) -> Dict[str, Any]:
    subject_counts: Counter[str] = Counter()
    weather_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()

    for f in clues:
        if f.subject:
            subject_counts[f.subject.lower()] += 1
        if f.weather:
            weather_counts[f.weather] += 1
        for t in (f.tags or []):
            name = getattr(t, "name", None) or getattr(t, "label", None) or t.get("name") if isinstance(t, dict) else None
            if name:
                tag_counts[name] += 1

    subject_echoes = [
        {"subject": s, "count": c}
        for s, c in subject_counts.items()
        if c > 1
    ]

    tag_echoes = [
        {"tag": t, "count": c}
        for t, c in tag_counts.items()
        if c > 1
    ]

    weather_echoes = [
        {"weather": w, "count": c}
        for w, c in weather_counts.items()
        if c > 1
    ]

    echo_intensity = len(subject_echoes) + len(tag_echoes) + len(weather_echoes)

    return {
        "subjects": subject_echoes,
        "tags": tag_echoes,
        "weather": weather_echoes,
        "intensity": echo_intensity,
    }


# ---------- Case linking + files ----------

def _link_clues_to_revelations(
    clues: List[NormalizedFragment],
    revelations: List[NormalizedFragment],
) -> Tuple[List[NormalizedFragment], List[NormalizedFragment]]:
    resolved_ids = set()

    for r in revelations:
        rs = (r.subject or "").lower()
        r_tags = set()
        for t in (r.tags or []):
            name = getattr(t, "name", None) or getattr(t, "label", None) or t.get("name") if isinstance(t, dict) else None
            if name:
                r_tags.add(name.lower())

        for c in clues:
            cs = (c.subject or "").lower()
            c_tags = set()
            for t in (c.tags or []):
                name = getattr(t, "name", None) or getattr(t, "label", None) or t.get("name") if isinstance(t, dict) else None
                if name:
                    c_tags.add(name.lower())

            subject_match = False
            if ":" in cs and ":" in rs:
                c_prefix = cs.split(":", 1)[1].strip()
                r_prefix = rs.split(":", 1)[1].strip()
                if c_prefix and r_prefix and c_prefix in rs:
                    subject_match = True

            tag_overlap = bool(c_tags & r_tags)

            if subject_match or tag_overlap:
                if getattr(c, "id", None) is not None:
                    resolved_ids.add(c.id)

    unresolved = [c for c in clues if getattr(c, "id", None) not in resolved_ids]
    resolved = [c for c in clues if getattr(c, "id", None) in resolved_ids]

    return unresolved, resolved


def _build_case_files(
    unresolved: List[NormalizedFragment],
) -> List[Dict[str, Any]]:
    clusters: Dict[str, List[NormalizedFragment]] = defaultdict(list)

    for c in unresolved:
        tag_names = []
        for t in (c.tags or []):
            name = getattr(t, "name", None) or getattr(t, "label", None) or t.get("name") if isinstance(t, dict) else None
            if name:
                tag_names.append(name)

        key = tag_names[0] if tag_names else (c.subject or "unknown")
        clusters[key].append(c)

    case_files: List[Dict[str, Any]] = []

    for key, items in clusters.items():
        weathers = Counter([i.weather for i in items if i.weather])
        dominant_weather = weathers.most_common(1)[0][0] if weathers else None

        subjects = [i.subject for i in items if i.subject]
        recent = sorted(
            items, key=lambda x: x.timestamp or datetime.min, reverse=True
        )[:3]

        case_files.append(
            {
                "symbol": key,
                "count": len(items),
                "dominant_weather": dominant_weather,
                "recent_subjects": subjects[:5],
                "recent": [
                    {
                        "subject": r.subject,
                        "date": r.date_raw,
                        "weather": r.weather,
                    }
                    for r in recent
                ],
            }
        )

    case_files.sort(key=lambda c: c["count"], reverse=True)
    return case_files


# ---------- Public API ----------

def analyze_detective(user_id: str) -> Dict[str, Any]:
    clues = _load_clues(user_id)
    revelations = _load_revelations(user_id)

    clues_by_type: Dict[str, List[NormalizedFragment]] = {}
    for f in clues:
        t = _extract_type_from_subject(f.subject, "Clue") or "unknown"
        clues_by_type.setdefault(t, []).append(f)

    rev_by_type: Dict[str, List[NormalizedFragment]] = {}
    for f in revelations:
        t = _extract_type_from_subject(f.subject, "Revelation") or "unknown"
        rev_by_type.setdefault(t, []).append(f)

    status_counts: Counter[str] = Counter()
    for f in clues:
        status = _status_from_subject(f.subject)
        status_counts[status] += 1

    symbols = _analyze_symbols(clues)
    weather = _analyze_weather(clues)
    echoes = _detect_echoes(clues)

    unresolved, resolved = _link_clues_to_revelations(clues, revelations)
    case_files = _build_case_files(unresolved)

    return {
        "clues": {
            "total": len(clues),
            "by_type": {k: len(v) for k, v in clues_by_type.items()},
            "recent": _recent(clues),
            "status": {
                "unresolved": status_counts.get("unresolved", 0),
                "integrated": status_counts.get("integrated", 0),
                "echoing": status_counts.get("echoing", 0),
                "unknown": status_counts.get("unknown", 0),
            },
        },
        "revelations": {
            "total": len(revelations),
            "by_type": {k: len(v) for k, v in rev_by_type.items()},
            "recent": _recent(revelations),
        },
        "symbols": symbols,
        "weather": weather,
        "echoes": echoes,
        "cases": {
            "unresolved_count": len(unresolved),
            "resolved_count": len(resolved),
            "files": case_files,
        },
    }
