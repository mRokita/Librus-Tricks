from datetime import datetime, timedelta


def get_next_monday(now=datetime.now()):
    for _ in range(8):
        if now.weekday() == 0:
            return now.date()
        now = now + timedelta(days=1)


def get_actual_monday(now=datetime.now()):
    for _ in range(8):
        if now.weekday() == 0:
            return now.date()
        now = now - timedelta(days=1)
