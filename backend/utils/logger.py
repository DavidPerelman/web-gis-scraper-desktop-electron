from datetime import datetime

def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_info(message: str):
    print(f"[INFO { _timestamp() }] {message}")

def log_warning(message: str):
    print(f"[WARN { _timestamp() }] {message}")

def log_error(message: str):
    print(f"[ERROR { _timestamp() }] {message}")

def log_debug(message: str):
    print(f"[DEBUG { _timestamp() }] {message}")
