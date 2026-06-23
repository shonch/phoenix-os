from fastapi import APIRouter, Depends
from phoenix_portfolio.backend.mongo_client import db
from phoenix_portfolio.phoenix_platform.auth import verify_token

# --- EXISTING ENGINES ---
from phoenix_portfolio.backend.engines.grief_engine import analyze_grief
from phoenix_portfolio.backend.engines.threshold_emerge_engine import analyze_thresholds
from phoenix_portfolio.backend.engines.detective_engine import analyze_detective

# --- NEW ENGINES (FULL BRAIN ACTIVATION) ---
from phoenix_portfolio.backend.engines.emotion_engine import analyze_emotion
from phoenix_portfolio.backend.engines.signal_engine import analyze_signals
from phoenix_portfolio.backend.engines.frisson_engine import analyze_frisson
from phoenix_portfolio.backend.engines.mirror_engine import analyze_mirror
from phoenix_portfolio.backend.engines.grind_engine import analyze_grind
from phoenix_portfolio.backend.engines.tag_engine import analyze_tags
from phoenix_portfolio.backend.engines.classifier_engine import analyze_classifiers
from phoenix_portfolio.backend.engines.dashboard_engine import analyze_dashboard
from phoenix_portfolio.backend.engines.phoenix_state_engine import analyze_phoenix_state

from phoenix_portfolio.backend.utils.state_serializer import StateSerializer


router = APIRouter(prefix="/phoenix/state", tags=["Phoenix State"])


def get_current_user_id(user_id: str = Depends(verify_token)):
    return {"user_id": user_id}


@router.get("/")
def get_state(user=Depends(get_current_user_id), limit: int = 200):
    uid = user["user_id"]

    # --- RAW COLLECTIONS ---
    raw_state = {
        "emotional_fragments": list(
            db["emotional_fragments"]
            .find({"user_id": uid})
            .sort("timestamp", -1)
            .limit(limit)
        ),
        "fragments": list(
            db["fragments"]
            .find({})
            .sort("timestamp", -1)
            .limit(limit)
        ),
        "symbolic_tags": list(
            db["symbolic_tags"]
            .find({"user_id": uid})
            .sort("timestamp", -1)
            .limit(limit)
        ),
        "clues": list(
            db["clues"]
            .find({"user_id": uid})
            .sort("timestamp", -1)
            .limit(limit)
        ),
        "thresholds": list(
            db["thresholds"]
            .find({"user_id": uid})
            .sort("date", -1)
            .limit(limit)
        ),
        "revelations": list(
            db["revelations"]
            .find({"user_id": uid})
            .sort("date", -1)
            .limit(limit)
        ),
        "module_status": list(
            db["module_status"]
            .find({"user_id": uid})
            .sort("timestamp", -1)
            .limit(limit)
        ),
    }

    # --- ANALYSIS LAYER (ALL ENGINES ONLINE) ---
    analysis = {
        "grief": analyze_grief(uid),
        "thresholds": analyze_thresholds(uid),
        "detective": analyze_detective(uid),
        "emotion": analyze_emotion(uid),
        "signals": analyze_signals(uid),
        "frisson": analyze_frisson(uid),
        "mirror": analyze_mirror(uid),
        "grind": analyze_grind(uid),
        "tags": analyze_tags(uid),
        "classifiers": analyze_classifiers(uid),
        "dashboard": analyze_dashboard(uid),
        "phoenix_state": analyze_phoenix_state(uid),
    }

    state = {
        "raw": raw_state,
        "analysis": analysis,
    }

    # ⭐ DEBUG BLOCK — TEMPORARY ⭐
    print("\n=== PHOENIX STATE DEBUG ===")
    print("analysis keys:", list(analysis.keys()))
    for key, value in analysis.items():
        print(f"  {key}: type={type(value)}, empty={value in (None, {}, [], '')}")
    print("raw keys:", list(raw_state.keys()))
    print("=== END PHOENIX STATE DEBUG ===\n")

    return StateSerializer(state).clean_ids(state)

