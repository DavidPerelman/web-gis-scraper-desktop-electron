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

    Returns:
    --------
    Path
        נתיב לקובץ ZIP שנוצר
    """
    temp_dir = tempfile.TemporaryDirectory()
    shapefile_dir = Path(temp_dir.name) / "shapefile"
    shapefile_dir.mkdir(parents=True, exist_ok=True)

    shapefile_path = shapefile_dir / "output.shp"
    gdf.to_file(shapefile_path)

    zip_path = Path(temp_dir.name) / "shapefile.zip"
    shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", shapefile_dir)

    return zip_path
