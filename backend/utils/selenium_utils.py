import time


def safe_click(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print("⚠️ Click failed:", e)
