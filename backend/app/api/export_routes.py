from fastapi import APIRouter
from backend.app.utils.gis_utils import build_gdf_from_plans
from backend.app.services.export_service import create_geojson_preview

router = APIRouter()


@router.post("/export/preview", summary="החזרת GeoJSON לתצוגה מקדימה")
async def export_preview(plans: list[dict]) -> dict:
    gdf = build_gdf_from_plans(plans)
    geojson = create_geojson_preview(gdf)
    return geojson
