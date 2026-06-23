# phoenix_portfolio/backend/engines/dashboard_engine.py

from typing import Any, Dict, List

from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.backend.utils.serialization import serialize_doc
from phoenix_portfolio.backend.engines.grief_engine import analyze_grief
from phoenix_portfolio.backend.engines.threshold_emerge_engine import analyze_thresholds
from phoenix_portfolio.backend.engines.detective_engine import analyze_detective


def _load_module_status(user_id: str) -> List[Dict[str, Any]]:
    docs = list(db["module_status"].find({"user_id": user_id}))
    return [serialize_doc(d) for d in docs]


def build_dashboard_state(user_id: str) -> Dict[str, Any]:
    grief_state = analyze_grief(user_id)
    thresholds_state = analyze_thresholds(user_id)
    detective_state = analyze_detective(user_id)
    modules = _load_module_status(user_id)

    return {
        "grief": grief_state,
        "thresholds": thresholds_state,
        "detective": detective_state,
        "modules": modules,
    }

def analyze_dashboard(user_id: str) -> Dict[str, Any]:
    """
    State-engine wrapper for build_dashboard_state.
    Provides a consistent interface for the Phoenix state engine.
    """
    return build_dashboard_state(user_id)

