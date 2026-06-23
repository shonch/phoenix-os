# phoenix_portfolio/backend/engines/phoenix_state_engine.py

from typing import Any, Dict, List

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc
from phoenix_portfolio.backend.engines.grief_engine import analyze_grief
from phoenix_portfolio.backend.engines.threshold_emerge_engine import analyze_thresholds
from phoenix_portfolio.backend.engines.detective_engine import analyze_detective
from phoenix_portfolio.backend.engines.frisson_engine import analyze_frisson


def _load_collection(name: str, user_id: str) -> List[Dict[str, Any]]:
    docs = list(db[name].find({"user_id": user_id}))
    return [serialize_doc(d) for d in docs]


def build_phoenix_state(user_id: str) -> Dict[str, Any]:
    emotional_fragments = _load_collection("emotional_fragments", user_id)
    thresholds = _load_collection("thresholds", user_id)
    clues = _load_collection("clues", user_id)
    revelations = _load_collection("revelations", user_id)
    symbolic_tags = _load_collection("symbolic_tags", user_id)
    promotion_log = _load_collection("promotion_log", user_id)
    module_status = _load_collection("module_status", user_id)
    fragments = _load_collection("fragments", user_id)
    raw_documents = (
        _load_collection("raw_documents", user_id)
        if "raw_documents" in db.list_collection_names()
        else []
    )

    grief_state = analyze_grief(user_id)
    thresholds_state = analyze_thresholds(user_id)
    detective_state = analyze_detective(user_id)
    frisson_state = analyze_frisson(user_id)

    # Build the final state object
    result = {
        "raw": {
            "emotional_fragments": emotional_fragments,
            "thresholds": thresholds,
            "clues": clues,
            "revelations": revelations,
            "symbolic_tags": symbolic_tags,
            "promotion_log": promotion_log,
            "module_status": module_status,
            "fragments": fragments,
            "raw_documents": raw_documents,
        },
        "analysis": {
            "grief": grief_state,
            "thresholds": thresholds_state,
            "detective": detective_state,
            "frisson": frisson_state,
        },
    }

    return result


def analyze_phoenix_state(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for build_phoenix_state.
    Provides the unified Phoenix state object expected by the router.
    """
    return build_phoenix_state(user_id)

