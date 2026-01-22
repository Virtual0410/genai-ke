# retrieval/recency.py

from datetime import datetime


def recency_score(published_date: str) -> float:
    """
    Compute recency score in range [0, 1].
    Newer documents score higher.
    """
    try:
        pub_date = datetime.strptime(published_date, "%Y-%m-%d")
    except ValueError:
        return 0.5  # fallback

    now = datetime.now()
    days_old = (now - pub_date).days

    # Cap at 5 years (1825 days)
    max_days = 1825
    days_old = min(days_old, max_days)

    # Newer = closer to 1
    return 1 - (days_old / max_days)
