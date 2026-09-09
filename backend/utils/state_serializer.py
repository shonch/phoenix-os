# phoenix_portfolio/backend/utils/state_serializer.py

from bson import ObjectId

class StateSerializer:
    """
    Phoenix Compatibility Layer — cleans MongoDB ObjectIds into plain
    strings so state can be safely returned as JSON.

    Note: this class previously included a normalize_* pipeline
    (to_state_v2, normalize_fragments, normalize_symbolic, etc.)
    meant to reshape raw Mongo data into a flat PhoenixStateV2 format.
    That pipeline read from a nested raw-state shape (symbolic_layer,
    threshold_layer, etc.) that the app never actually produces —
    phoenix_state_routes.py builds its own flat raw_state directly and
    only ever calls .clean_ids() on it. Removed as dead code.
    """

    def __init__(self, raw_state):
        self.raw = raw_state or {}

    def clean_ids(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, list):
            return [self.clean_ids(x) for x in obj]
        if isinstance(obj, dict):
            return {k: self.clean_ids(v) for k, v in obj.items()}
        return obj
