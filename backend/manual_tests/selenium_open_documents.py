# 1. אתחול webdriver
# 2. מעבר לכתובת pl_url (שים כתובת קבועה ידנית)
# 3. המתנה לטעינה (h1.plan-name)
# 4. שימוש ב־XPath כדי ללחוץ על "מסמכי התכנית"
# 5. הדפסה – הצלחה או שגיאה

import os
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

# from utils.logger import log_info, log_warning


def wait_for_download(directory, timeout=10):
    for _ in range(timeout):
        files = os.listdir(directory)
        if any(f.endswith(".pdf") for f in files):
            return os.path.join(directory, [f for f in files if f.endswith(".pdf")][0])
        time.sleep(1)
    return None


def run() -> dict:
    pdf_path = None
    # url = "https://mavat.iplan.gov.il/SV4/1/1000351135/310"
    url = "https://mavat.iplan.gov.il/SV4/1/1000262173/310"

    download_dir = tempfile.mkdtemp()

    prefs = {
        "download.default_directory": download_dir,  # תיקיית הורדה
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,  # לא לפתוח PDF בדפדפן
    }

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 7).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.plan-name"))
    )

    documents_section_opened = False
    approved_section_opened = False
    instructions_section_opened = False
    download_button_clicked = False
    file_downloaded = False

    try:
        documents_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@role='button' and descendant::span[normalize-space(.)='מסמכי התכנית']]",
                )
            )
        )
        documents_button.click()
        documents_section_opened = True
        print("documents_button clicked")
        time.sleep(2)
    except Exception as e:
        print("approved_documents_button failed:", e)

    if documents_section_opened:
        wait = WebDriverWait(driver, 10)

        try:
            approved_section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'uk-accordion-title') and .//span[contains(normalize-space(.), 'מסמכים מאושרים')]]",
                    )
                )
            )

            driver.execute_script("arguments[0].click();", approved_section)
            approved_section_opened = True
            print("נלחץ מקטע 'מסמכים מאושרים'")
            print("approved_documents_button clicked")
        except Exception as e:
            print("approved_documents_button failed:", e)

        if approved_section_opened:
            try:
                instructions_section = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[contains(@class,'uk-accordion-title') and .//span[normalize-space(.)='הוראות']]",
                        )
                    )
                )

                driver.execute_script("arguments[0].click();", instructions_section)
                print("instructions_button clicked")
                instructions_section_opened = True
            except Exception as e:
                print("instructions_button failed:", e)

        if instructions_section_opened:
            try:
                download_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//span[contains(text(),'הוראות התכנית')]/ancestor::li//div[contains(@class,'clickable')]",
                        )
                    )
                )

                driver.execute_script("arguments[0].click();", download_button)
                print("download_button clicked")
                download_button_clicked = True
            except Exception as e:
                print("download_button failed:", e)

        if download_button_clicked:
            try:
                pdf_path = wait_for_download(download_dir)

                if pdf_path:
                    print("file download:", pdf_path)
                    file_downloaded = True
                else:
                    print("download failed")

            except Exception as e:
                print("download_button failed:", e)
    else:
        print("skipped clicking approved_documents_button because section didn't open")

    # time.sleep(2)

    input("לחץ Enter כדי לסגור את הדפדפן...")
    driver.quit()

    return pdf_path


if __name__ == "__main__":
    run()
