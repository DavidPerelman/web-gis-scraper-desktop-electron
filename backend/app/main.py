from fastapi import FastAPI

from backend.routes import polygon_routes


app = FastAPI(
    title="GIS Scraper API",
    description="API לקבלת פוליגון, ביצוע גרידת נתונים והחזרת שכבת תוצאה",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(polygon_routes.router)
