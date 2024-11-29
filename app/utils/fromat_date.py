import datetime

import pytz


def format_date(date: str) -> str:
    date = datetime.datetime.fromisoformat(date)
    date = date.replace(tzinfo=pytz.utc)
    date = date.astimezone(pytz.timezone("Asia/Kolkata"))
    return date.strftime("%b %d %I:%M %p")
