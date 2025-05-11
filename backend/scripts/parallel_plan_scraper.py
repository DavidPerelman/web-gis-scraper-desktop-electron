import asyncio
import pycurl
import json
from io import BytesIO
from backend.app.services.mavat_scraper import extract_main_fields_async
from asyncio import Semaphore

# קובעים מגבלה למספר תוכניות שירוצו במקביל
semaphore = Semaphore(5)

# עדכון 2025-05-11:
# נוספה הרצה מקבילית של תוכניות באמצעות extract_main_fields_async
# שופרו זמני הטעינה ע"י קיצור timeout והסרת המתנות מיותרות בפונקציית הגירוד
# פונקציה זו משתמשת ב־pycurl כדי לעקוף בעיות SSL בחיבור אל ags.iplan.gov.il


def fetch_plans_by_bbox(
    minx: float, miny: float, maxx: float, maxy: float
) -> list[dict]:
    geometry = (
        f"%7B%22xmin%22%3A{minx}%2C%22ymin%22%3A{miny}%2C%22xmax%22%3A{maxx}%2C%22ymax%22%3A{maxy}%2C"
        f"%22spatialReference%22%3A%7B%22wkid%22%3A2039%7D%7D"
    )
    full_url = (
        "https://ags.iplan.gov.il/arcgisiplan/rest/services/PlanningPublic/Xplan/MapServer/1/query"
        "?f=json"
        "&where=pl_area_dunam%20%3C%3D15"
        "&returnGeometry=true"
        f"&geometry={geometry}"
        "&geometryType=esriGeometryEnvelope"
        "&inSR=2039"
        "&outFields=pl_number%2Cpl_name%2Cpl_url%2Cquantity_delta_120%2Cstation_desc%2Cplan_county_name"
        "&orderByFields=pl_number"
        "&outSR=2039"
    )

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


async def scrape_by_bbox(minx, miny, maxx, maxy) -> dict:
    print("📥 Fetching plans from API with BBOX...")
    plans = fetch_plans_by_bbox(minx, miny, maxx, maxy)
    print(f"📦 Total plans fetched: {len(plans)}")

    results = await asyncio.gather(*[limited_scrape(plan) for plan in plans])
    print("✅ Scraping complete.")

    return {"type": "FeatureCollection", "features": results}


if __name__ == "__main__":
    # דוגמה להרצה ידנית
    bbox = (220042.1933, 632101.8472, 220802.8864, 632677.6837)
    asyncio.run(scrape_by_bbox(*bbox))
