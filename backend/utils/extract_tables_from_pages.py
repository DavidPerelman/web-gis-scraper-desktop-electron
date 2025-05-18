import pandas as pd
import pdfplumber

from suppress_stderr import suppress_stderr
from table_cleaner import clean_dataframe


def generate_column_names_from_three_rows(
    row1: list, row2: list, row3: list
) -> list[str]:
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


def extract_tables_from_pages(pdf_path: str, pages: list) -> list[list[str]]:
    pages = sorted(set(pages))
    headers = []
    all_rows = []
    with suppress_stderr():
        with pdfplumber.open(pdf_path) as pdf:
            for i, page_num in enumerate(sorted(set(pages))):
                page = pdf.pages[page_num - 1]
                table = page.extract_table()
                if not table:
                    continue  # אם אין טבלה – דלג

                row1 = table[0]
                row2 = table[1]
                row3 = table[2]

                column_names = generate_column_names_from_three_rows(row1, row2, row3)

                all_rows.extend(table[3:])
                headers = column_names
    df = pd.DataFrame(all_rows, columns=headers)
    df = clean_dataframe(df)

    df[df.columns[::-1]].to_csv(
        "טבלת_זכויות_101-0135004.csv", index=False, encoding="utf-8-sig"
    )
    print("✅ הטבלה נשמרה בהצלחה ל־CSV עם כיווניות RTL")

    return df
