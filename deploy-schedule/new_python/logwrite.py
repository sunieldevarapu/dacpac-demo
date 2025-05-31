def log(message: str) -> str:
    """Writes to log file"""
    with open("log.txt", "a") as line:
        line.write(message)
