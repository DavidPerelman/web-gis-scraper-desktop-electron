import geopandas as gpd
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection


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
            # print(
            #     f"⚠️ Failed to build polygon for {plan['attributes'].get('pl_number')}: {e}"
            # )
            continue

    collection = FeatureCollection(features)
    gdf = gpd.GeoDataFrame.from_features(collection, crs="EPSG:2039")
    return gdf
