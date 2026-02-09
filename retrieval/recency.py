"""
Recency scoring for documents.
"""
from datetime import datetime

def recency_score(published_date: str) -> float:
    """
    Compute recency score in range [0, 1].
    Newer documents score higher.
    
    Args:
        published_date: Date string in format "YYYY-MM-DD" or "unknown"
    
    Returns:
        Float between 0 and 1 (1 = most recent)
    """
    # Handle unknown/missing dates
    if not published_date or published_date == "unknown":
        return 0.5  # Neutral score for unknown dates
    
    try:
        pub_date = datetime.strptime(published_date, "%Y-%m-%d")
    except ValueError:
        # Try alternative formats
        try:
            pub_date = datetime.strptime(published_date, "%Y/%m/%d")
        except ValueError:
            return 0.5  # fallback for unparseable dates

    now = datetime.now()
    days_old = (now - pub_date).days
    
    # Handle future dates (shouldn't happen but be defensive)
    if days_old < 0:
        return 1.0

    # Cap at 5 years (1825 days)
    max_days = 1825
    days_old = min(days_old, max_days)

    # Newer = closer to 1
    return 1 - (days_old / max_days)
