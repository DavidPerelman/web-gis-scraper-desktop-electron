import pycurl
import json
from io import BytesIO
import geopandas as gpd
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection

from backend.app.services.mavat_scraper import (
    extract_main_fields_sync,
)


class IplanFetcher:
    def __init__(self, polygon_gdf: gpd.GeoDataFrame):
        self.polygon = polygon_gdf
        self.bbox = self.polygon.total_bounds
        self.plans = []

    async def fetch_plans_by_bbox(self) -> dict:
        minx, miny, maxx, maxy = self.bbox
        url = (
            "https://ags.iplan.gov.il/arcgisiplan/rest/services/PlanningPublic/Xplan/MapServer/1/query"
            "?f=json"
            "&where=pl_area_dunam%20%3C%3D15"
            "&returnGeometry=true"
            f"&geometry=%7B%22xmin%22%3A{minx}%2C%22ymin%22%3A{miny}%2C%22xmax%22%3A{maxx}%2C%22ymax%22%3A{maxy}%2C%22spatialReference%22%3A%7B%22wkid%22%3A2039%7D%7D"
            "&geometryType=esriGeometryEnvelope"
            "&inSR=2039"
            "&outFields=pl_number%2Cpl_name%2Cpl_url%2Cquantity_delta_120%2Cstation_desc%2Cplan_county_name"
            "&orderByFields=pl_number"
            "&outSR=2039"
        )

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.TIMEOUT, 20)
        c.setopt(c.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)
        c.setopt(
            c.HTTPHEADER,
            [
                "Accept: application/json",
                "Content-Type: application/x-www-form-urlencoded",
            ],
        )
        c.perform()
        c.close()

        response_body = buffer.getvalue().decode("utf-8")
        return json.loads(response_body)

    def filter_plans_in_polygon(self, raw_json: dict) -> list[dict]:
        features = raw_json.get("features", [])
        filtered = []

        for plan in features:
            geom_data = plan.get("geometry", {})
            rings = geom_data.get("rings")
            if not rings:
                continue
            polygon = Polygon(shell=rings[0], holes=rings[1:])
            if self.polygon.unary_union.contains(polygon.centroid):
                filtered.append(plan)
        return filtered

    def extract_mavat_data(self, plan: dict) -> dict:
        return extract_main_fields_sync(plan)

    def build_geodataframe_feature_collection(
        self, plans: list[dict]
    ) -> gpd.GeoDataFrame:
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

    async def run(self) -> list[dict]:
        raw = await self.fetch_plans_by_bbox()
        filtered = self.filter_plans_in_polygon(raw)

        filtered_subset = filtered[:5]

        enriched = []

        for plan in filtered_subset:
            plan = self.extract_mavat_data(plan)
            enriched.append(plan)

        return enriched
