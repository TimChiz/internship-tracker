from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# The one time zone the whole app runs on. Our users are US students,
# so a deadline of "Oct 23" means Oct 23 on the US East Coast.
APP_TIMEZONE = ZoneInfo("America/New_York")

def app_now() -> datetime:
    """The current New York time, without timezone info (SQLite stores times without it)."""
    return datetime.now(APP_TIMEZONE).replace(tzinfo=None)