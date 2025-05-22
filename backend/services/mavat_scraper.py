"""
שירות לגירוד נתונים כמותיים מדף תוכנית באתר מבא"ת (mavat.iplan.gov.il)
"""

import tempfile
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

from utils.selenium_utils import safe_click
from utils.table_cleaner import normalize_label
from utils.extract_quantitative_table import extract_quantitative_table
from utils.extract_tables_from_pages import extract_tables_from_pages
from services.download_plan_instructions_pdf import download_plan_instructions_pdf
from utils.logger import log_info, log_warning
from utils.quantitative_field_map import hebrew_label_to_key


def is_blocked_page(driver: webdriver.Chrome) -> bool:
    return "לא ניתן לצפות בפרטי היישות" in driver.page_source


def extract_main_fields_sync(plan: dict) -> dict:
    try:
        url = plan["attributes"].get("pl_url")
        if not url:
            return plan

        download_dir = tempfile.mkdtemp()

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
        }
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        if is_blocked_page(driver):
            log_warning(
                f"🔒 תוכנית חסומה: {plan.get('attributes', {}).get('pl_number')}"
            )
            plan["attributes"]["blocked"] = True
            plan["attributes"]["enrichment_failed"] = True

            return plan  # בלי לנסות להמשיך לגרד

        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.plan-name"))
        )

        try:
            wait = WebDriverWait(driver, 10)
            more_button = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button[aria-label='נתונים נוספים']")
                )
            )

            if more_button.is_displayed() and more_button.is_enabled():
                safe_click(driver, more_button)
                time.sleep(1)  # זמן קצר לטעינה
            else:
                log_info(
                    "'More Data' button is not visible or not enabled – skipping click."
                )
        except (
            TimeoutException,
            NoSuchElementException,
            ElementNotInteractableException,
        ):
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

            normalized_label = normalize_label(label)
            key = hebrew_label_to_key.get(normalized_label)

            if key:
                plan["attributes"][key] = value
            else:
                print("Not found after normalize:", repr(normalized_label))
                print(f"label raw: {repr(label)}")
                print(f"normalized: {repr(normalized_label)}")
                print(f"not in keys: {list(hebrew_label_to_key.keys())}")
                log_warning(f"Unrecognized field label: {label}")

        plan["attributes"]["quant_data"] = quant_data

        plan["attributes"].pop("quant_data", None)

        pdf_path = download_plan_instructions_pdf(driver, download_dir)

        header_keywords = [
            "םוקמ / ןיינב",
            "שרגמ לדוג",
            "הינב יחטש",
            'ד"חי רפסמ',
        ]

        if not pdf_path:
            plan["attributes"]["quantitative_table"] = None
        else:
            pages = extract_quantitative_table(pdf_path, header_keywords)
            if not pages:
                plan["attributes"]["quantitative_table"] = None
            else:
                df = extract_tables_from_pages(pdf_path, pages)
                if df.columns.duplicated().any():
                    dupes = df.columns[df.columns.duplicated()].unique()
                    log_warning(f"⚠️ Duplicate columns found and removed: {dupes}")
                    df = df.loc[:, ~df.columns.duplicated()]

                mapped_rows = []
                for row in df.to_dict(orient="records"):
                    new_row = {}
                    for heb_key, val in row.items():
                        normalized_label = normalize_label(heb_key)
                        key = hebrew_label_to_key.get(normalized_label)
                        if key:
                            new_row[key] = val
                        else:
                            log_warning(f"עמודה שלא מופתה: {normalized_label}")

                    mapped_rows.append(new_row)

                plan["attributes"]["quantitative_table_raw"] = df.to_dict(
                    orient="records"
                )
                plan["attributes"]["quantitative_table"] = mapped_rows

    finally:
        driver.quit()

    return plan
