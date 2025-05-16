"""
שירות לגירוד נתונים כמותיים מדף תוכנית באתר מבא"ת (mavat.iplan.gov.il)
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)
from bs4 import BeautifulSoup

from utils.logger import log_info, log_warning

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
    "ב - תחבורה - רק\"ל (מס' תחנות)": "lrt_station_count",
    'ב - תחבורה - רק"ל (ק"מ)': "lrt_km",
}


def extract_main_fields_sync(plan: dict) -> dict:
    url = plan["attributes"].get("pl_url")
    if not url:
        return plan

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 7).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.plan-name"))
    )

    try:
        wait = WebDriverWait(driver, 10)
        more_button = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button[aria-label='נתונים נוספים']")
        ))

        if more_button.is_displayed() and more_button.is_enabled():
            more_button.click()
            time.sleep(1)  # זמן קצר לטעינה
        else:
            log_info("'More Data' button is not visible or not enabled – skipping click.")
    except (TimeoutException, NoSuchElementException, ElementNotInteractableException):
        log_warning("'More Data' button not found or not clickable.")

    html = driver.page_source

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
        log_warning("BeautifulSoup: Failed to extract total area in dunams:", e)

    quant_data = []

    quant_data_div = small_div.find_all(
        "button",
        {"class": "uk-accordion-title"},
    )

    for button in quant_data_div:
        label_div = button.find("div", class_="uk-width-expand")
        label = label_div.get_text(strip=True) if label_div else ""

        value_div = button.find_next("div", class_="uk-width-1-2 uk-text-left")
        value = value_div.find("b").get_text(strip=True) if value_div else ""

        unit_div = button.find_next("div", class_="uk-width-1-6")
        unit = unit_div.get_text(strip=True) if unit_div else ""

        quant_data.append({"label": label, "value": value, "unit": unit})

        key = label_to_key.get(label)
        if key:
            plan["attributes"][key] = value
        else:
            log_warning(f"Unrecognized field label: {label}")

    plan["attributes"]["quant_data"] = quant_data

    plan["attributes"].pop("quant_data", None)

    driver.quit()

    return plan
