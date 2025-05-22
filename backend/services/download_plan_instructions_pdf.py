import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.selenium_utils import safe_click


def wait_for_download(directory, timeout=10):
    for _ in range(timeout):
        files = os.listdir(directory)
        if any(f.endswith(".pdf") for f in files):
            return os.path.join(directory, [f for f in files if f.endswith(".pdf")][0])
        time.sleep(1)
    return None


def download_plan_instructions_pdf(driver, download_dir: str) -> str:
    documents_section_opened = False
    approved_section_opened = False
    instructions_section_opened = False
    download_button_clicked = False
    approved_section = None

    try:
        documents_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@role='button' and descendant::span[normalize-space(.)='מסמכי התכנית']]",
                )
            )
        )

        safe_click(driver, documents_button)

        documents_section_opened = True
        print("documents_button clicked")
        time.sleep(2)
    except Exception as e:
        print("approved_documents_button failed:", e)

    if documents_section_opened:
        WebDriverWait(driver, 10)

        try:
            approved_section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'uk-accordion-title') and .//span[contains(normalize-space(.), 'מסמכים מאושרים')]]",
                    )
                )
            )

            safe_click(driver, approved_section)
            approved_section_opened = True
            print("approved_documents_button clicked")
        except Exception as e:
            print("approved_documents_button failed:", e)

        try:
            approved_section = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'uk-accordion-title') and .//span[contains(normalize-space(.), 'מסמכים בתהליך')]]",
                    )
                )
            )

            safe_click(driver, approved_section)
            approved_section_opened = True
            print("approved_documents_button clicked")
        except Exception as e:
            print("approved_documents_button failed:", e)
            approved_section = None

        if approved_section_opened or approved_section is None:
            try:
                instructions_section = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[contains(@class,'uk-accordion-title') and .//span[normalize-space(.)='הוראות']]",
                        )
                    )
                )

                safe_click(driver, instructions_section)
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

                safe_click(driver, download_button)
                print("download_button clicked")
                download_button_clicked = True
            except Exception as e:
                print("download_button failed:", e)

        if download_button_clicked:
            try:
                if download_dir:
                    return wait_for_download(download_dir)
                else:
                    print("download failed")
                    return None

            except Exception as e:
                print("download_button failed:", e)
    else:
        print("skipped clicking approved_documents_button because section didn't open")
