# phoenix_portfolio/backend/utils/state_serializer.py

from bson import ObjectId

class StateSerializer:
    """
    Phoenix Compatibility Layer — Normalizes raw Phoenix Engine output
    into a clean, flat, predictable PhoenixStateV2 format.
    """

    def __init__(self, raw_state):
        self.raw = raw_state or {}

    # ------------------------------------------------------------
    # UNIVERSAL OBJECTID CLEANER
    # ------------------------------------------------------------
    def clean_ids(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, list):
            return [self.clean_ids(x) for x in obj]
        if isinstance(obj, dict):
            return {k: self.clean_ids(v) for k, v in obj.items()}
        return obj

    # ------------------------------------------------------------
    # FRAGMENT NORMALIZATION
    # ------------------------------------------------------------
    def normalize_fragment(self, doc):
        if not doc:
            return None

        content = (
            doc.get("content")
            or doc.get("body")
            or doc.get("text")
            or ""
        )

        return {
            "id": str(doc.get("_id")),
            "title": (
                doc.get("title")
                or doc.get("subject")
                or doc.get("header")
                or "Untitled Fragment"
            ),
            "content": content,
            "tags": doc.get("tags") or [],
            "timestamp": (
                doc.get("timestamp")
                or doc.get("created_at")
                or doc.get("inserted_at")
            ),
            "type": doc.get("type") or "unknown",
            "weather": doc.get("weather"),
            "preview": content[:120],
        }

    def normalize_fragments(self):
        frags = self.raw.get("fragments", [])
        return [self.normalize_fragment(f) for f in frags if f]

    # ------------------------------------------------------------
    # SYMBOLIC NORMALIZATION
    # ------------------------------------------------------------
    def normalize_symbolic(self):
        symbolic = self.raw.get("symbolic_layer", {})

        promotion_log = symbolic.get("promotion_log", [])
        symbolic_tags = symbolic.get("symbolic_tags", [])
        tag_index_docs = symbolic.get("tag_index", [])

        # Convert tag_index_docs (list of docs) → dict
        tag_index = {}
        for entry in tag_index_docs:
            tag = entry.get("tag")
            if tag:
                tag_index[tag] = tag_index.get(tag, 0) + 1

        return {
            "symbolic_tags": symbolic_tags,
            "tag_index": tag_index,
            "promotion_log": promotion_log,
        }

    # ------------------------------------------------------------
    # SYSTEM NORMALIZATION
    # ------------------------------------------------------------
    def normalize_system(self):
        system = self.raw.get("system_layer", {})
        return system.get("module_status", [])

    # ------------------------------------------------------------
    # THRESHOLD NORMALIZATION
    # ------------------------------------------------------------
    def normalize_thresholds(self):
        thresh = self.raw.get("threshold_layer", {})
        return {
            "thresholds": thresh.get("thresholds", []),
            "revelations": thresh.get("revelations", []),
        }

    # ------------------------------------------------------------
    # EMOTIONAL NORMALIZATION
    # ------------------------------------------------------------
    def normalize_emotional(self):
        emo = self.raw.get("emotional_state", {})
        return {
            "engine_v1": emo.get("engine_v1", []),
            "legacy_fragments": emo.get("legacy_fragments", []),
        }

    # ------------------------------------------------------------
    # MYTHIC FALLBACK
    # ------------------------------------------------------------
    def normalize_mythic(self):
        return {
            "dominant_archetype": "Unknown",
            "active_modes": [],
            "resonance_score": 0,
            "notes": "Mythic engine not yet implemented.",
        }

    # ------------------------------------------------------------
    # FINAL ASSEMBLY
    # ------------------------------------------------------------
    def to_state_v2(self):
        symbolic = self.normalize_symbolic()
        thresholds = self.normalize_thresholds()

        state_v2 = {
            "fragments": self.normalize_fragments(),
            "emotional_fragments": self.normalize_emotional()["legacy_fragments"],
            "symbolic_tags": symbolic["symbolic_tags"],
            "tag_index": symbolic["tag_index"],
            "promotion_log": symbolic["promotion_log"],
            "module_status": self.normalize_system(),
            "thresholds": thresholds["thresholds"],
            "revelations": thresholds["revelations"],
            "mythic_state": self.normalize_mythic(),
            "raw": self.raw,
        }

        return self.clean_ids(state_v2)

