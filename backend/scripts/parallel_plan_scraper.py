import asyncio
import time
import pycurl
import json
from io import BytesIO
from backend.app.services.mavat_scraper import extract_main_fields_async
from asyncio import Semaphore

# קובעים מגבלה למספר תוכניות שירוצו במקביל
semaphore = Semaphore(5)

minx = 220042.1933
miny = 632101.8472
maxx = 220802.8864
maxy = 632677.6837

full_url = (
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


def fetch_plans_from_api():
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, full_url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)
    curl.setopt(
        pycurl.HTTPHEADER,
        [
            "Accept: application/json",
            "Content-Type: application/json",
        ],
    )
    curl.perform()
    curl.close()

    body = buffer.getvalue().decode("utf-8")
    data = json.loads(body)
    return data.get("features", [])


async def limited_scrape(plan: dict) -> dict:
    async with semaphore:
        return await extract_main_fields_async(plan)


async def scrape_all():
    print("📥 Fetching plans from API...")
    plans = fetch_plans_from_api()
    print(f"📦 Total plans fetched: {len(plans)}")

    start = time.time()
    results = await asyncio.gather(*[limited_scrape(plan) for plan in plans])
    end = time.time()

    print(f"✅ Scraping complete. Duration: {end - start:.2f} seconds.")
    return results


if __name__ == "__main__":
    asyncio.run(scrape_all())
