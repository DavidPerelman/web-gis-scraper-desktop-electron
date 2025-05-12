from pathlib import Path
import geopandas as gpd


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
    pass
