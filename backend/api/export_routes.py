import os
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks
from utils.gis_utils import build_gdf_from_plans
from services.export_service import (
    create_geojson_preview,
    create_shapefile_zip,
)
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/export/preview", summary="החזרת GeoJSON לתצוגה מקדימה")
async def export_preview(plans: list[dict]) -> dict:
    gdf = build_gdf_from_plans(plans)
    gdf = gdf.to_crs("EPSG:4326")
    geojson = create_geojson_preview(gdf)

    return geojson


@router.post("/export/download", summary="הורדת קובץ ZIP עם Shapefile")
async def export_download(plans: list[dict], background_tasks: BackgroundTasks):
    gdf = build_gdf_from_plans(plans)
    zip_path = create_shapefile_zip(gdf)

    def cleanup_file(path: Path):
        try:
            os.remove(path)
            # נוכל למחוק גם את התיקייה אם רוצים: os.rmdir(path.parent)
        except Exception as e:
            print(f"⚠️ Failed to delete temp file: {e}")

    background_tasks.add_task(cleanup_file, zip_path)

    return FileResponse(
        path=zip_path, media_type="application/zip", filename="plans_export.zip"
    )
