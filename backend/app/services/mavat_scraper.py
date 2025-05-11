"""
שירות לגירוד נתונים כמותיים מדף תוכנית באתר מבא"ת (mavat.iplan.gov.il)
"""

from pyppeteer import launch


async def extract_main_fields_async(plan: dict) -> dict:
    url = plan["attributes"].get("pl_url")
    if not url:
        return plan

    browser = await launch(
        headless=False,
        executablePath="C:\Program Files\Google\Chrome\Application\chrome.exe",
        args=["--no-sandbox"],
    )
    page = await browser.newPage()

    try:
        await page.goto(url, timeout=60000)
        # בשלב הבא נגרד את הנתונים מהעמוד
    finally:
        await browser.close()

    return plan
