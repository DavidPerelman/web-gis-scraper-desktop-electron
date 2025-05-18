# 1. אתחול webdriver
# 2. מעבר לכתובת pl_url (שים כתובת קבועה ידנית)
# 3. המתנה לטעינה (h1.plan-name)
# 4. שימוש ב־XPath כדי ללחוץ על "מסמכי התכנית"
# 5. הדפסה – הצלחה או שגיאה

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


def run() -> dict:
    url = "https://mavat.iplan.gov.il/SV4/1/1000351135/310"

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 7).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.plan-name"))
    )

    documents_section_opened = False
    approved_section_opened = False
    instructions_section_opened = False

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
    else:
        print("skipped clicking approved_documents_button because section didn't open")

    # time.sleep(2)

    input("לחץ Enter כדי לסגור את הדפדפן...")
    driver.quit()


if __name__ == "__main__":
    run()
