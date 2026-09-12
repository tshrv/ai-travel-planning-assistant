from datetime import datetime, timedelta, timezone


def get_current_timestamp() -> str:
    """Get current timestamp in format yyyymmddhhmmss"""
    dt = datetime.now(tz=timezone(offset=timedelta(hours=5, minutes=30)))
    return dt.strftime("%Y%m%d%H%M%S")