from fastapi import APIRouter
from backend.app.utils.gis_utils import build_gdf_from_plans
from backend.app.services.export_service import (
    create_geojson_preview,
    create_shapefile_zip,
)
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/export/preview", summary="החזרת GeoJSON לתצוגה מקדימה")
async def export_preview(plans: list[dict]) -> dict:
    gdf = build_gdf_from_plans(plans)
    geojson = create_geojson_preview(gdf)
    return geojson


@router.post("/export/download", summary="הורדת קובץ ZIP עם Shapefile")
async def export_download(plans: list[dict]):
    gdf = build_gdf_from_plans(plans)
    zip_path = create_shapefile_zip(gdf)
    return FileResponse(
        path=zip_path, media_type="application/zip", filename="plans_export.zip"
    )
