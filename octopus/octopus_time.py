from datetime import datetime, timedelta

# Schedule 5 minutes from now
queue_time = (datetime.utcnow() + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
queue_expiry = (datetime.utcnow() + timedelta(minutes=65)).strftime("%Y-%m-%dT%H:%M:%SZ")
