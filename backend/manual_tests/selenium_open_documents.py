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

        driver.execute_script(
            "arguments[0].style.border='3px solid red'", documents_button
        )

        print("succeesfuly clickd!")

    except (TimeoutException, NoSuchElementException, ElementNotInteractableException):
        print("'documents_button' button not found or not clickable.")

    # time.sleep(2)

    input("⬅️ לחץ Enter כדי לסגור את הדפדפן...")
    driver.quit()


if __name__ == "__main__":
    run()
