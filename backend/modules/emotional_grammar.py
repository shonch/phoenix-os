# phoenix_portfolio/backend/modules/emotional_grammar.py

from datetime import datetime
import random
import requests


# Fallback quotes if the API is unreachable
FALLBACK_QUOTES = [
    "“In the ashes of today, tomorrow learns to breathe.”",
    "“Nothing sacred is ever truly lost.”",
    "“You are allowed to begin again.”",
    "“Every threshold is a teacher.”",
    "“The self you are becoming is already reaching back for you.”",
]


def fetch_quote() -> str:
    """
    Fetch a quote from a public quote API.
    Falls back to local quotes if offline.
    """
    try:
        # Quotable API (stable, JSON)
        response = requests.get("https://api.quotable.io/random", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return f"“{data.get('content', '').strip()}” — {data.get('author', 'Unknown')}"
    except Exception:
        pass

    # Fallback
    return random.choice(FALLBACK_QUOTES)


def build_fragment(content: str,
                   title: str | None,
                   subject: str | None,
                   fragment_type: str | None,
                   tags: list[dict]) -> dict:
    """
    Canonical emotional grammar for Phoenix ingestion.
    Produces expressive, mythic, emotionally resonant fragments.
    """

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    quote = fetch_quote()

    # Determine type
    ftype = fragment_type or "emotional_log"

    # Determine title
    ftitle = title or (subject or "Untitled Fragment")

    # Build expressive content
    expressive_content = f"""
### 🔥 Phoenix Fragment — {ftitle}

**Type**: {ftype}  
**Timestamp**: {now}  
**Tags**: {", ".join([t.get("label", "") for t in tags])}

---

{content}

---

### 🕊️ Closing Thought  
{quote}
"""

    return {
        "type": ftype,
        "title": ftitle,
        "subject": subject,
        "content": expressive_content.strip(),
    }

