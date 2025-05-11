import json
import requests
import pycurl
from io import BytesIO


def fetch_plans_by_bbox(bbox: tuple) -> dict:
    minx, miny, maxx, maxy = bbox
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
