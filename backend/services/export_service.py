from datetime import datetime
import json
from pathlib import Path
import uuid
import geopandas as gpd
import tempfile
import shutil


def create_geojson_preview(gdf: gpd.GeoDataFrame) -> dict:
    """
    ממירה GeoDataFrame לאובייקט GeoJSON לצורך תצוגה מקדימה.

    Parameters:
    -----------
    gdf : GeoDataFrame
        שכבת המידע שעובדה (למשל מתוך התוצאה של fetch_plans)

    Returns:
    --------
    dict
        מילון במבנה FeatureCollection (GeoJSON תקני)
    """
    geojson_str = gdf.to_json(ensure_ascii=False)
    geojson_dict = json.loads(geojson_str)
    return geojson_dict


def create_shapefile_zip(gdf: gpd.GeoDataFrame) -> Path:
    """
    יוצר קובץ ZIP הכולל Shapefile מתוך GeoDataFrame.
    מחזיר נתיב לקובץ ה־ZIP.

    יש למחוק את הקובץ לאחר השליחה (הוא לא נמחק אוטומטית).
    """
    temp_dir_path = Path(tempfile.mkdtemp())
    shapefile_dir = temp_dir_path / "shapefile"
    shapefile_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = str(uuid.uuid4())[:6]

    shapefilename = f"plans_data_{timestamp}_{uid}.shp"

    shapefile_path = shapefile_dir / shapefilename
    gdf.to_file(shapefile_path, encoding="utf-8")

    cpg_path = shapefile_path.with_suffix(".cpg")
    cpg_path.write_text("UTF-8", encoding="utf-8")
    
    zipfilename = f"plans_data_{timestamp}_{uid}.zip"

    zip_path = temp_dir_path / zipfilename
    shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", shapefile_dir)

    return zip_path
