# phoenix_portfolio/backend/engines/detective_engine.py

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter, defaultdict

from backend.mongo_client import db
from backend.utils.adapter import (
    NormalizedFragment,
    normalize_fragment,
)


# ---------- Data loading ----------

def _load_detective_fragments(user_id: str) -> List[NormalizedFragment]:
    """Real Detective fragments — ground truth via type field."""
    docs = list(db["revelations"].find({"user_id": user_id, "type": "detective"}))
    return [normalize_fragment(d, "revelations") for d in docs]


def _load_other_revelations(user_id: str) -> List[NormalizedFragment]:
    """Mirror/Emerge fragments, used only for real tag-based resolution
    linking — never mixed into the primary Detective count."""
    docs = list(db["revelations"].find({"user_id": user_id, "type": {"$ne": "detective"}}))
    return [normalize_fragment(d, "revelations") for d in docs]


# ---------- Parsing helpers ----------

def _recent(fs: List[NormalizedFragment], limit: int = 10) -> List[Dict[str, Any]]:
    return [
        {
            "id": getattr(f, "id", None),
            "subject": f.subject,
            "date": f.date_raw,
            "weather": f.weather,
            "snippet": (f.content or "")[:160],
        }
        for f in sorted(fs, key=lambda x: x.timestamp or datetime.min, reverse=True)[:limit]
    ]


def _tag_names(f: NormalizedFragment) -> set:
    return {str(t).lower() for t in (f.tags or []) if t}

# ---------- Symbolic + echo analysis ----------

def _analyze_symbols(clues: List[NormalizedFragment]) -> Dict[str, Any]:
    tag_counts: Counter[str] = Counter()
    pair_counts: Counter[Tuple[str, str]] = Counter()
    archetype_counts: Counter[str] = Counter()

    for f in clues:
        tag_names = list(_tag_names(f))
        print("DEBUG symbolic_density — fragment tags:", f.tags, "-> extracted:", tag_names)
        tag_counts.update(tag_names)

        for t in (f.tags or []):
            archetype = getattr(t, "archetype", None) or (t.get("archetype") if isinstance(t, dict) else None)
            if archetype:
                archetype_counts[archetype] += 1

        unique_tags = sorted(tag_names)
        for i in range(len(unique_tags)):
            for j in range(i + 1, len(unique_tags)):
                pair_counts[(unique_tags[i], unique_tags[j])] += 1

    return {
        "top_tags": [{"tag": t, "count": c} for t, c in tag_counts.most_common(10)],
        "top_pairs": [{"tags": [a, b], "count": c} for (a, b), c in pair_counts.most_common(10)],
        "top_archetypes": [{"archetype": a, "count": c} for a, c in archetype_counts.most_common(10)],
        "symbolic_density": len(tag_counts),
    }


def _analyze_weather(clues: List[NormalizedFragment]) -> Dict[str, Any]:
    weather_counts: Counter[str] = Counter()
    for f in clues:
        if f.weather:
            weather_counts[f.weather] += 1

    return {
        "distribution": [{"weather": w, "count": c} for w, c in weather_counts.most_common()],
    }


def _detect_echoes(clues: List[NormalizedFragment]) -> Dict[str, Any]:
    subject_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()

    for f in clues:
        if f.subject:
            subject_counts[f.subject.lower()] += 1
        for name in _tag_names(f):
            tag_counts[name] += 1

    subject_echoes = [{"subject": s, "count": c} for s, c in subject_counts.items() if c > 1]
    tag_echoes = [{"tag": t, "count": c} for t, c in tag_counts.items() if c > 1]

    return {
        "subjects": subject_echoes,
        "tags": tag_echoes,
        "intensity": len(subject_echoes) + len(tag_echoes),
    }


# ---------- Case linking + files ----------

def _link_clues_to_revelations(
    clues: List[NormalizedFragment],
    revelations: List[NormalizedFragment],
) -> Tuple[List[NormalizedFragment], List[NormalizedFragment]]:
    """
    Resolved means real tag overlap (2+ shared real tags) with another
    fragment — deliberate data the user attached, not a coincidental
    subject-name match (most fragments share Symbolic Anchor names by
    chance, which made the old subject-text matching unreliable).
    """
    resolved_ids = set()

    for c in clues:
        c_tags = _tag_names(c)
        if len(c_tags) < 2:
            continue

        for r in revelations:
            r_tags = _tag_names(r)
            overlap = c_tags & r_tags
            if len(overlap) >= 2:
                if getattr(c, "id", None) is not None:
                    resolved_ids.add(c.id)
                break

    unresolved = [c for c in clues if getattr(c, "id", None) not in resolved_ids]
    resolved = [c for c in clues if getattr(c, "id", None) in resolved_ids]

    return unresolved, resolved


def _build_case_files(unresolved: List[NormalizedFragment]) -> List[Dict[str, Any]]:
    clusters: Dict[str, List[NormalizedFragment]] = defaultdict(list)

    for c in unresolved:
        tag_names = sorted(_tag_names(c))
        key = tag_names[0] if tag_names else (c.subject or "unknown")
        clusters[key].append(c)

    case_files: List[Dict[str, Any]] = []
    for key, items in clusters.items():
        weathers = Counter([i.weather for i in items if i.weather])
        dominant_weather = weathers.most_common(1)[0][0] if weathers else None
        recent = sorted(items, key=lambda x: x.timestamp or datetime.min, reverse=True)[:3]

        case_files.append({
            "symbol": key,
            "count": len(items),
            "dominant_weather": dominant_weather,
            "recent": [
                {"subject": r.subject, "date": r.date_raw, "weather": r.weather}
                for r in recent
            ],
        })

    case_files.sort(key=lambda c: c["count"], reverse=True)
    return case_files


# ---------- Public API ----------

def analyze_detective(user_id: str) -> Dict[str, Any]:
    clues = _load_detective_fragments(user_id)
    other_revelations = _load_other_revelations(user_id)

    symbols = _analyze_symbols(clues)
    weather = _analyze_weather(clues)
    echoes = _detect_echoes(clues)

    unresolved, resolved = _link_clues_to_revelations(clues, other_revelations)
    case_files = _build_case_files(unresolved)

    return {
        "total": len(clues),
        "fragments": _recent(clues, limit=len(clues) or 1),
        "symbols": symbols,
        "weather": weather,
        "echoes": echoes,
        "cases": {
            "unresolved_count": len(unresolved),
            "resolved_count": len(resolved),
            "files": case_files,
        },
    }
