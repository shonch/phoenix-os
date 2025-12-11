# phoenix_engine/utils/tag_utils.py

from datetime import datetime

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def calculate_score(tag: dict) -> float:
    """
    Calculates promotion score for a tag based on weighted factors.
    Handles string values gracefully (e.g., 'neutral').
    """
    frequency_score = min(tag.get("usage_count", 0) / 10, 1.0)
    emotional_weight_score = safe_float(tag.get("emotional_weight", 0)) / 10
    user_count_score = len(set(tag.get("user_ids", []))) / 5

    created_at = tag.get("created_at")
    recency_score = 0.5
    if created_at:
        try:
            days_old = (datetime.utcnow() - datetime.fromisoformat(created_at)).days
            recency_score = 1.0 if days_old < 7 else 0.5
        except Exception:
            pass

    return (frequency_score * 0.4 +
            emotional_weight_score * 0.3 +
            user_count_score * 0.2 +
            recency_score * 0.1)

def promote_tag(tag: dict, tag_index_collection, promotion_log_collection) -> dict:
    """
    Promotes a tag into tag_index if score >= 0.7.
    Records the promotion in promotion_log.
    """
    score = calculate_score(tag)
    status = "promoted" if score >= 0.7 else "candidate"

    promoted_doc = {
        "tag_id": tag["tag_id"],
        "tag_name": tag["tag_name"],
        "user_ids": tag.get("user_ids", []),
        "promoted_from": tag["_id"],
        "promotion_score": score,
        "promotion_status": status,
        "last_promoted_at": datetime.utcnow().isoformat() if status == "promoted" else None,
        "version": tag.get("version", 1)
    }

    # Insert or update in tag_index
    tag_index_collection.update_one(
        {"tag_id": tag["tag_id"]},
        {"$set": promoted_doc},
        upsert=True
    )

    # Log promotion
    log_promotion(promoted_doc, promotion_log_collection)

    return promoted_doc


def log_promotion(promoted_doc: dict, promotion_log_collection) -> None:
    """
    Writes an entry to promotion_log for auditing.
    """
    log_entry = {
        "tag_id": promoted_doc["tag_id"],
        "tag_name": promoted_doc["tag_name"],
        "promotion_score": promoted_doc["promotion_score"],
        "promotion_status": promoted_doc["promotion_status"],
        "timestamp": datetime.utcnow().isoformat(),
        "user_ids": promoted_doc.get("user_ids", [])
    }
    promotion_log_collection.insert_one(log_entry)
