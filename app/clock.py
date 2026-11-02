from datetime import datetime, timezone

def utc_now() -> datetime:
    """
    Returns the current time in UTC, because we want to use UTC everywhere in the app and not convert time zones

    """