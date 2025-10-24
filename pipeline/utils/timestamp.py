from datetime import datetime, timezone, timedelta

# Philippine Time (UTC+8)
LOCAL = timezone(timedelta(hours=8))

def right_now():
    """Return current timestamp in Philippine Time (ISO format)."""
    return datetime.now(LOCAL).isoformat()

def hours_ago(hours: int):
    """Return timestamp N hours ago in Philippine Time (ISO format)."""
    return (datetime.now(LOCAL) - timedelta(hours=hours)).isoformat()
