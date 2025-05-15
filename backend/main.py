import os
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api import export_routes
from api.routes import router

app_dir = getattr(sys, '_MEIPASS', os.path.abspath("."))
os.environ["PATH"] = os.pathsep.join([
    os.environ.get("PATH", ""),
    os.path.join(app_dir, "fiona.libs"),
    os.path.join(app_dir, "fiona"),
    os.path.join(app_dir, "gdal"),  # אם קיים
    os.path.join(app_dir, "Shapely.libs"),
])

app = FastAPI(
    title="GIS Scraper API",
    description="API לקבלת פוליגון, ביצוע גרידת נתונים והחזרת שכבת תוצאה",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # או ["*"] לפיתוח
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def main():
    return JSONResponse(content={"status": "ok"})


@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})


app.include_router(router)
app.include_router(export_routes.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
