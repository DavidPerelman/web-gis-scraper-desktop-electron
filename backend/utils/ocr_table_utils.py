import os
import re
import pandas as pd
from .quantitative_field_map import hebrew_label_to_key
from .table_cleaner import normalize_label


def save_ocr_text(text: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def load_ocr_text(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def load_ocr_pages_from_folder(folder: str) -> dict[int, str]:
    pages = {}
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".txt") and filename.startswith("page_"):
            try:
                page_num = int(filename.replace("page_", "").replace(".txt", ""))
                with open(os.path.join(folder, filename), encoding="utf-8") as f:
                    pages[page_num] = f.read()
            except Exception as e:
                print(f"⚠️ שגיאה בקריאת {filename}: {e}")
    return pages


def find_table_page_ranges(ocr_pages: dict[int, str]) -> list[tuple[int, int]]:
    start_marker = "טבלת זכויות והוראות בניה - מצב מוצע"
    end_marker = "האמור בטבלה זו גובר"

    ranges = []
    current_start = None

    sorted_pages = sorted(ocr_pages.keys())

    for page_num in sorted_pages:
        text = ocr_pages[page_num]

        if start_marker in text and current_start is None:
            current_start = page_num

        if end_marker in text and current_start is not None:
            ranges.append((current_start, page_num))
            current_start = None

    if current_start is not None:
        ranges.append((current_start, current_start))

    return ranges


def extract_table_from_range(
    start: int, end: int, ocr_pages: dict[int, str]
) -> list[str]:
    table_lines = []
    started = False

    for page_num in range(start, end + 1):
        text = ocr_pages.get(page_num, "")
        lines = text.strip().splitlines()

        for line in lines:
            if "טבלת זכויות" in line or "מצב מוצע" in line:
                started = True
                continue  # לא לכלול את שורת הכותרת עצמה

            if "האמור בטבלה זו גובר" in line:
                started = False
                break  # עצור כשמגיעים לסוף

            if started:
                table_lines.append(line.strip())

    return [line for line in table_lines if line]


def merge_header_lines(header_lines: list[str]) -> list[str]:
    merged = []
    buffer = ""

    for line in header_lines:
        line = line.strip()
        if not line:
            continue

        if buffer:
            if len(line.split()) <= 4:
                buffer += " / " + line
            else:
                merged.append(buffer)
                buffer = line
        else:
            buffer = line

    if buffer:
        merged.append(buffer)

    return merged


def detect_data_start_index(lines: list[str], min_numeric: int = 6) -> int:
    """
    מוצאת את האינדקס שבו מתחילים הערכים בטבלה,
    לפי הופעה של שורה עם הרבה ערכים מספריים/טקסטואליים קצרים.
    """
    for i, line in enumerate(lines):
        tokens = re.findall(r"[\d.]+|[\u0590-\u05FF]+", line)
        if len(tokens) >= min_numeric:
            return i
    return -1


def extract_table_dataframe_from_lines(
    table_lines: list[str], expected_columns: int = 18
) -> pd.DataFrame:
    """
    חותך את שורות הטבלה אנכית, כאשר הערכים מופיעים לפני הכותרות (כפי ש-Google OCR מחלץ לעיתים).
    """
    if len(table_lines) < expected_columns * 2:
        raise ValueError(f"❌ הקלט קצר מדי — צריך לפחות {expected_columns * 2} שורות.")

    value_lines = [line.strip() for line in table_lines[:expected_columns]]
    header_lines = [
        line.strip() for line in table_lines[expected_columns : expected_columns * 2]
    ]

    mapped_headers = [
        hebrew_label_to_key.get(normalize_label(h), normalize_label(h))
        for h in header_lines
    ]

    return pd.DataFrame([value_lines], columns=mapped_headers)


if __name__ == "__main__":
    folder = r"C:\Users\dpere\Documents\python-projects\web-gis-scraper-desktop-electron\backend\utils\pdf_images-101-0175604"
    ocr_pages = load_ocr_pages_from_folder(folder)

    table_ranges = find_table_page_ranges(ocr_pages)

    if not table_ranges:
        raise ValueError("❌ לא נמצאו טבלאות בקובץ הזה.")

    start, end = table_ranges[0]
    table_lines = extract_table_from_range(start, end, ocr_pages)

    df = extract_table_dataframe_from_lines(table_lines)

    print(df.T)
