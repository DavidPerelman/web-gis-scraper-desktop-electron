import sys
from datetime import datetime
from pathlib import Path

IS_EXE = getattr(sys, 'frozen', False)
LOG_PATH = Path("log.txt")

def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_warning(message: str):
    _log("WARN", message)

def log_info(message: str):
    _log("INFO", message)

def log_error(message: str):
    _log("ERROR", message)

def _log(level: str, message: str):
    ts = _timestamp()
    line = f"[{level} {ts}] {message}"

    if IS_EXE:
        # ב־EXE – לא נדפיס אימוג'ים ולא נשתמש בעברית
        try:
            LOG_PATH.write_text("", encoding="utf-8", errors="ignore") if not LOG_PATH.exists() else None
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            # fallback לקונסולה רק אם אפשר
            try:
                print(f"[{level} {ts}] Failed to write log file: {e}")
            except:
                pass
    else:
        try:
            print(line)
        except UnicodeEncodeError:
            print(f"[{level} {ts}] [Unprintable message]")
