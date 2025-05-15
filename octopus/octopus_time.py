from datetime import datetime, timedelta, timezone

queue_time = (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
queue_expiry = (datetime.now(timezone.utc) + timedelta(minutes=65)).strftime("%Y-%m-%dT%H:%M:%SZ")
