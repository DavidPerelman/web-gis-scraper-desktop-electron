import geopandas as gpd
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection


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
        exterior = rings[0]
        holes = rings[1:]

        try:
            polygon = Polygon(shell=exterior, holes=holes)
            feature = Feature(geometry=polygon, properties=plan["attributes"])
            features.append(feature)
        except Exception as e:
            # log_warning(
            #     f"⚠️ Failed to build polygon for {plan['attributes'].get('pl_number')}: {e}"
            # )
            continue

    collection = FeatureCollection(features)

    gdf = gpd.GeoDataFrame.from_features(collection, crs="EPSG:2039")
    gdf.rename(columns=field_renames, inplace=True)

    return gdf
