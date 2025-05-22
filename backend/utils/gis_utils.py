import geopandas as gpd
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection
import pandas as pd

field_renames = {
    "residential_units": "res_units",
    "residential_sqm": "res_sqm",
    "small_residential_units": "small_res",
    "commercial_sqm": "com_sqm",
    "employment_sqm": "emp_sqm",
    "public_bldg_sqm": "pub_sqm",
    "hotel_rooms": "h_rooms",
    "hotel_sqm": "hotel_sqm",
    "total_area_dunam": "area_dunam",
    "quantity_delta_120": "approv_unit",
    "station_desc": "status",
    "plan_county_name": "district",
}


def build_gdf_from_plans(plans: list[dict]) -> gpd.GeoDataFrame:
    features = []

    for plan in plans:
        rings = plan.get("geometry", {}).get("rings", [])
        if not rings:
            continue

        try:
            polygon = Polygon(shell=rings[0], holes=rings[1:])
            feature = Feature(geometry=polygon, properties=plan["attributes"])
            features.append(feature)
        except Exception as e:
            print(f"⚠️ Failed to convert polygon: {e}")
            continue

    collection = FeatureCollection(features)

    # צור טבלה רגילה ואז המר ל-GeoDataFrame עם עמודת geometry מוגדרת
    geometries = [
        Polygon(f["geometry"]["coordinates"][0]) for f in collection["features"]
    ]
    properties = [f["properties"] for f in collection["features"]]

    df = pd.DataFrame(properties)
    df["geometry"] = geometries
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:2039")
    gdf.rename(columns=field_renames, inplace=True)

    return gdf
