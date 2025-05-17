import pdfplumber
import pandas as pd
import sys
import os
import contextlib

pdf_path = r"C:\Users\dpere\Documents\python-projects\web-gis-scraper-desktop-electron\backend\101-0925198_תדפיס הוראות התכנית_חתום לאישור_1.pdf"

search_phrase = "טבלת זכויות והוראות בניה"


@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


def find_table_start_page(pdf_path: str, phrase: str) -> int | None:
    with suppress_stderr():
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and phrase in text:
                    return i
        return None


def extract_raw_table_from_pdf(pdf_path: str, start_page: int) -> pd.DataFrame:
    """
    מחלץ טבלה גולמית מ־PDF החל מעמוד מסוים.
    ממשיך עמוד אחר עמוד עד שאין טבלאות.
    לא מניח מראש את שמות העמודות – מחזיר DataFrame גולמי.
    """
    all_rows = []

    with suppress_stderr():
        with pdfplumber.open(pdf_path) as pdf:
            page_index = start_page
            while page_index < len(pdf.pages):
                page = pdf.pages[page_index]
                tables = page.extract_tables()

                if not tables:
                    break

                return tables


start_page = find_table_start_page(pdf_path, search_phrase[::-1])

table = extract_raw_table_from_pdf(pdf_path, start_page)
row1 = table[1][0]
row2 = table[1][1]
row3 = table[1][2]
row4 = table[1][3]


def generate_column_names_from_three_rows(
    row1: list, row2: list, row3: list
) -> list[str]:
    """
    מחזירה שמות עמודות לפי שלוש שורות כותרת, עם היפוך טקסט מלא לעברית.
    """

    def clean(val):
        return str(val).replace("\n", " ").strip() if val else None

    def reverse(val):
        return val[::-1] if val else val

    def identify_split_columns_with_mapping(row: list) -> dict:
        split_columns = []
        main_columns = []
        split_to_main = {}
        temp_main = None
        temp_splits = []

        for idx, cell in enumerate(row):
            if cell is not None:
                if temp_main is not None and temp_splits:
                    main_columns.append(temp_main)
                    for split_idx in temp_splits:
                        split_to_main[split_idx] = temp_main
                temp_main = idx
                temp_splits = []
            else:
                split_columns.append(idx)
                temp_splits.append(idx)

        if temp_main is not None and temp_splits:
            main_columns.append(temp_main)
            for split_idx in temp_splits:
                split_to_main[split_idx] = temp_main

        return {
            "main_columns": main_columns,
            "split_columns": split_columns,
            "split_to_main": split_to_main,
        }

    mapping = identify_split_columns_with_mapping(row1)
    split_to_main = mapping["split_to_main"]

    column_names = []
    for idx in range(len(row1)):
        main_val = clean(row1[idx])
        mid_val = clean(row2[idx]) if idx < len(row2) else None
        sub_val = clean(row3[idx]) if idx < len(row3) else None

        if idx in split_to_main:
            main_idx = split_to_main[idx]
            main_val = clean(row1[main_idx])
            mid_val = clean(row2[idx]) or clean(row2[main_idx])
            sub_val = clean(row3[idx]) or clean(row3[main_idx])

        parts = [main_val, mid_val, sub_val]
        parts = [reverse(p) for p in parts if p]
        name = " / ".join(parts)
        column_names.append(name)

    return column_names


column_names = generate_column_names_from_three_rows(row1, row2, row3)

import re


def is_hebrew(text: str) -> bool:
    return bool(re.search(r"[\u0590-\u05FF]", text))


def clean_cell(cell: str | None) -> str | None:
    if not cell:
        return None

    # ניקוי בסיסי
    cell = str(cell).replace("\n", " ").strip()

    # הסרה של מילות רעש (כמו "מונה", "מונה הדפסה" וכו')
    junk_words = ["מונה", "הנומ", "מונה הדפסה", "הצפסה הנומ"]
    for junk in junk_words:
        cell = cell.replace(junk, "").strip()

    # אם אחרי ההסרה לא נשאר כלום – נוותר על התא
    if not cell:
        return None

    # הפוך רק אם הטקסט בעברית
    return cell[::-1] if is_hebrew(cell) else cell


def extract_table_rows_after_headers(pdf_path: str, start_page: int) -> list[list[str]]:
    rows = []
    with suppress_stderr():
        with pdfplumber.open(pdf_path) as pdf:
            page_index = start_page
            while page_index < len(pdf.pages):
                page = pdf.pages[page_index]
                tables = page.extract_tables()

                if not tables:
                    break  # אין טבלה – מפסיקים לקרוא

                for table in tables:
                    if len(table) <= 3:
                        continue  # פחות מ־3 שורות – אין ערכים

                    # אם זו הפעם הראשונה – נדלג על שלוש כותרות
                    raw_rows = table[3:] if page_index == start_page else table

                    for row in raw_rows:
                        cleaned_row = [clean_cell(cell) for cell in row]
                        rows.append(cleaned_row)

                page_index += 1
    return rows


search_phrase = "טבלת זכויות והוראות בניה"[::-1]
start_page = find_table_start_page(pdf_path, search_phrase)

if start_page is not None:
    data_rows = extract_table_rows_after_headers(pdf_path, start_page)

df = pd.DataFrame(data_rows, columns=column_names)
df.to_dict()
