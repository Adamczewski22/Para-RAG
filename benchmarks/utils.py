from datetime import datetime

def parse_locomo_timestamp(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%I:%M %p on %d %B, %Y")
