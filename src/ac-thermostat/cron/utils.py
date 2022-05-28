from datetime import datetime


def log(msg):
    """Logs provided messsage with prepended timestamp"""
    timestamp = datetime.now().isoformat(" ", "seconds")
    return f"[{timestamp}] {msg}"