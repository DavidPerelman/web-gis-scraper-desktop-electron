import pdfplumber
import contextlib
import os
import sys
import pandas as pd


class PdfTableExtractor:
    @staticmethod
    def extract_table_from_pdf(pdf_path: str) -> pd.DataFrame:
        """
        מחזירה את טבלת הזכויות מקובץ PDF כ־DataFrame.
        """
        # שלב 1: חיפוש עמוד תחילת הטבלה
        start_page = PdfTableExtractor._find_table_start_page(pdf_path)
        if start_page is None:
            raise ValueError("לא נמצאה טבלת זכויות בקובץ")

        # שלב 2: חילוץ שלוש שורות כותרת
        header_rows = PdfTableExtractor._extract_header_rows(pdf_path, start_page)
        column_names = PdfTableExtractor._generate_column_names(*header_rows)

        column_keywords = set(c.split(" / ")[-1] for c in column_names)

        # שלב 3: חילוץ שורות הנתונים
        data_rows = PdfTableExtractor._extract_data_rows(
            pdf_path, start_page, column_keywords
        )

        # שלב 4: בניית טבלה
        return pd.DataFrame(data_rows, columns=column_names)

    @staticmethod
    @contextlib.contextmanager
    def _suppress_stderr():
        with open(os.devnull, "w") as devnull:
            old_stderr = sys.stderr
            sys.stderr = devnull
            try:
                yield
            finally:
                sys.stderr = old_stderr

    @staticmethod
    def _find_table_start_page(pdf_path: str) -> int | None:
        search_phrase = "טבלת זכויות והוראות בניה"[::-1]  # חיפוש בטקסט הפוך
        with PdfTableExtractor._suppress_stderr():
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and search_phrase in text:
                        return i
            return None

    @staticmethod
    def _extract_header_rows(
        pdf_path: str, start_page: int
    ) -> tuple[list[str], list[str], list[str]]:
        with PdfTableExtractor._suppress_stderr():
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[start_page]
                tables = page.extract_tables()

                for table in tables:
                    if len(table) >= 3:
                        return table[0], table[1], table[2]

                raise ValueError("לא נמצאו שלוש שורות כותרת באף טבלה בעמוד")

    @staticmethod
    def _generate_column_names(row1: list, row2: list, row3: list) -> list[str]:
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

    @staticmethod
    def _extract_data_rows(
        pdf_path: str, start_page: int, column_keywords: set[str]
    ) -> list[list[str]]:
        import re

        def is_hebrew(text: str) -> bool:
            return bool(re.search(r"[\u0590-\u05FF]", text))

        def clean_cell(cell: str | None) -> str | None:
            if not cell:
                return None
            cell = str(cell).replace("\n", " ").strip()
            junk_words = ["מונה", "הנומ", "מונה הדפסה", "הצפסה הנומ", "תכנון", "ןונכת"]
            for junk in junk_words:
                cell = cell.replace(junk, "").strip()
            return cell[::-1] if is_hebrew(cell) else cell if cell else None

        def is_comment_row(row: list[str]) -> bool:
            joined = " ".join(filter(None, row)).strip()
            return (
                len([cell for cell in row if cell]) <= 2
                and len(joined) > 40
                and any(
                    w in joined for w in ["הוראות", "הערות", "תכנית", "מגורים", "שטחים"]
                )
            )

        def is_header_like_row(row: list[str]) -> bool:
            headers = {
                'מספר יח"ד',
                "קומות",
                "שטחי בניה",
                "יעוד",
                "שימוש",
                "תאי שטח",
                "בניין / מקום",
            }
            return any(
                cell and any(header in cell for header in headers) for cell in row
            )

        rows = []
        with PdfTableExtractor._suppress_stderr():
            with pdfplumber.open(pdf_path) as pdf:
                page_index = start_page
                while page_index < len(pdf.pages):
                    page = pdf.pages[page_index]
                    tables = page.extract_tables()

                    if not tables:
                        break

                    for table in tables:
                        if len(table) < 3:
                            continue

                        # זיהוי האם מדובר בטבלת המשך (עמוד חדש + שורת כותרת שדומה לקודמת)
                        first_row = table[0]
                        is_continuation = any(
                            cell and any(keyword in cell for keyword in column_keywords)
                            for cell in first_row
                        )

                        # נחלץ את השורות לפי העמוד:
                        if page_index == start_page:
                            raw_rows = table[3:]
                        elif is_continuation:
                            raw_rows = table[3:]
                        else:
                            continue  # לא טבלת המשך ולא בעמוד ראשון – לא רלוונטי

                        for row in raw_rows:
                            if is_comment_row(row) or is_header_like_row(row):
                                return rows
                            cleaned_row = [clean_cell(cell) for cell in row]
                            rows.append(cleaned_row)

                    page_index += 1

        return rows


pdf_path = r"C:\Users\dpere\Documents\python-projects\web-gis-scraper-desktop-electron\backend\101-0135004_תדפיס הוראות התכנית_חתום לאישור_1.pdf"
# pdf_path = r"C:\Users\dpere\Documents\python-projects\web-gis-scraper-desktop-electron\backend\101-0925198_תדפיס הוראות התכנית_חתום לאישור_1.pdf"
df = PdfTableExtractor.extract_table_from_pdf(pdf_path)
print(df)
