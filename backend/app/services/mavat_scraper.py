"""
שירות לגירוד נתונים כמותיים מדף תוכנית באתר מבא"ת (mavat.iplan.gov.il)
"""

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

label_to_key = {
    'מגורים (יח"ד)': "residential_units",
    'מגורים (מ"ר)': "residential_sqm",
    'מסחר (מ"ר)': "commercial_sqm",
    'תעסוקה (מ"ר)': "employment_sqm",
    'מבני ציבור (מ"ר)': "public_bldg_sqm",
    "חדרי מלון / תיירות (חדר)": "hotel_rooms",
    'חדרי מלון / תיירות (מ"ר)': "hotel_sqm",
    'סה"כ שטח בדונם': "total_area_dunam",
    'דירות קטנות (יח"ד)': "small_residential_units",
}


async def extract_main_fields_async(plan: dict) -> dict:
    url = plan["attributes"].get("pl_url")
    if not url:
        return plan

    print("🔗 Trying to open:", url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("h1.plan-name", timeout=10000)

            btn_more = page.locator("button[aria-label='נתונים נוספים']")

            try:
                if await btn_more.count() > 0 and await btn_more.is_visible():
                    await btn_more.scroll_into_view_if_needed()
                    await btn_more.click()
                    await page.wait_for_timeout(1000)  # המתן לטעינת שדות נוספים

                html = await page.content()

                soup = BeautifulSoup(html, "html.parser")

                quant_data_block = soup.find(
                    "li",
                    {"class": "sv4-icon-arrow uk-open uk-hide-arrow ng-star-inserted"},
                )

                quant_data_block_div = quant_data_block.find(
                    "div",
                    {"class": "uk-accordion-content uk-margin-remove"},
                )

                small_div = quant_data_block_div.find(
                    "div",
                    {"class": "uk-padding-small"},
                )

                try:
                    dunam_div = small_div.find(
                        "div",
                        {"class": "uk-grid uk-grid-collapse sv4-headline"},
                    )
                    dunam_blocks_divs = dunam_div.find_all(
                        "div",
                        {"class": "uk-width-1-2"},
                    )
                    dunam_value_div = dunam_blocks_divs[1]

                    plan["attributes"]["total_area_dunam"] = dunam_value_div.find(
                        "div", {"class": "sv4-big"}
                    ).get_text(strip=True)
                except Exception as e:
                    print('⚠️ BeautifulSoup: לא הצלחנו לשלוף סה"כ שטח בדונם:', e)

                quant_data = []

                quant_data_div = small_div.find_all(
                    "button",
                    {"class": "uk-accordion-title"},
                )

                for button in quant_data_div:
                    label_div = button.find("div", class_="uk-width-expand")
                    label = label_div.get_text(strip=True) if label_div else ""

                    value_div = button.find_next(
                        "div", class_="uk-width-1-2 uk-text-left"
                    )
                    value = (
                        value_div.find("b").get_text(strip=True) if value_div else ""
                    )

                    unit_div = button.find_next("div", class_="uk-width-1-6")
                    unit = unit_div.get_text(strip=True) if unit_div else ""

                    quant_data.append({"label": label, "value": value, "unit": unit})

                    key = label_to_key.get(label)
                    if key:
                        plan["attributes"][key] = value
                    else:
                        print(f"⚠️ שדה לא מזוהה: {label}")

                plan["attributes"]["quant_data"] = quant_data
            except Exception as e:
                print("⚠️ לא ניתן ללחוץ על כפתור 'נתונים נוספים':", e)

        except Exception as e:
            print("❌ Page.goto error:", e)
            return plan
    return plan
