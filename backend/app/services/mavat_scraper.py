"""
שירות לגירוד נתונים כמותיים מדף תוכנית באתר מבא"ת (mavat.iplan.gov.il)
"""

from playwright.async_api import async_playwright


async def extract_main_fields_async(plan: dict) -> dict:
    url = plan["attributes"].get("pl_url")
    if not url:
        return plan

    print("🔗 Trying to open:", url)

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, timeout=60000)
            print("✅ Page loaded successfully.")
        except Exception as e:
            print("❌ Page.goto error:", e)
            return plan

    return plan
