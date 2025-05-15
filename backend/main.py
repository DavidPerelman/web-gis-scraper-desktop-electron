from fastapi import FastAPI
from backend.app.api import export_routes
from backend.app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware


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


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(router)
app.include_router(export_routes.router)
