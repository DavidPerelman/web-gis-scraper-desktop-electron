"""
שירות לגירוד נתונים כמותיים מדף תוכנית באתר מבא"ת (mavat.iplan.gov.il)
"""

from playwright.async_api import async_playwright


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
            print("✅ Page loaded successfully.")
            await page.wait_for_selector("h1.plan-name", timeout=15000)
            print("✅ Contnet page loaded successfully.")

            # await page.wait_for_selector("button.uk-accordion-title", timeout=10000)

            btn_more = page.locator("button[aria-label='נתונים נוספים']")

            try:
                if await btn_more.count() > 0 and await btn_more.is_visible():
                    await btn_more.scroll_into_view_if_needed()
                    await btn_more.click()
                    await page.wait_for_timeout(1000)  # המתן לטעינת שדות נוספים

                try:
                    area_row = page.locator(
                        "div.sv4-headline", has_text='סה"כ שטח בדונם'
                    )
                    value = await area_row.locator("div.sv4-big").text_content()
                    if value:
                        plan["attributes"]["total_area_dunam"] = value.strip()
                except Exception as e:
                    print('⚠️ לא הצלחנו לשלוף סה"כ שטח בדונם:', e)

                # גרידת כל הנתונים הכמותיים
                quant_data = []

                items = page.locator("button.uk-accordion-title")
                count = await items.count()

                for i in range(count):
                    item = items.nth(i)

                    try:
                        # label
                        label_div = item.locator(".uk-width-expand")
                        label = await label_div.text_content() or ""
                        label = label.strip()

                        # value
                        value_div = item.locator("b")
                        value = await value_div.text_content() or ""
                        value = value.strip()

                        # unit
                        unit_div = item.locator(".sv4-small")
                        unit = await unit_div.text_content() or ""
                        unit = unit.strip()

                        quant_data.append(
                            {"label": label, "value": value, "unit": unit}
                        )

                        plan["attributes"]["quant_data"] = quant_data

                    except Exception as e:
                        print(f"⚠️ שגיאה בפריט {i}: {e}")

            except Exception as e:
                print("⚠️ לא ניתן ללחוץ על כפתור 'נתונים נוספים':", e)

        except Exception as e:
            print("❌ Page.goto error:", e)
            return plan

    # print(plan)
    return plan
