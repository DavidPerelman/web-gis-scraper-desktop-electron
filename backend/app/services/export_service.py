import json
from pathlib import Path
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
    geojson_str = gdf.to_json()
    geojson_dict = json.loads(geojson_str)
    return geojson_dict


def create_shapefile_zip(gdf: gpd.GeoDataFrame) -> Path:
    """
    יוצר קובץ ZIP הכולל Shapefile מתוך GeoDataFrame.
    מחזיר נתיב לקובץ ה־ZIP.

    יש למחוק את הקובץ לאחר השליחה (הוא לא נמחק אוטומטית).
    """
    temp_dir_path = Path(tempfile.mkdtemp())  # לא נמחק אוטומטית
    shapefile_dir = temp_dir_path / "shapefile"
    shapefile_dir.mkdir(parents=True, exist_ok=True)

    shapefile_path = shapefile_dir / "output.shp"
    gdf.to_file(shapefile_path)

    zip_path = temp_dir_path / "shapefile.zip"
    shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", shapefile_dir)

    return zip_path
