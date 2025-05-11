# run_dev.py
import asyncio
import sys
import uvicorn

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
