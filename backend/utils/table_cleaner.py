# utils/table_cleaner.py

import re
import pandas as pd


def reverse_hebrew_words_only(text: str) -> str:
    if not isinstance(text, str):
        return text

    tokens = re.split(r"(\s+)", text)  # שמור רווחים
    reversed_tokens = []

    for token in tokens:
        if re.search(r"[\u0590-\u05FF]", token):  # אם יש עברית
            reversed_tokens.append(token[::-1])
        else:
            reversed_tokens.append(token)  # השאר כמו שהוא

    return "".join(reversed_tokens)


def clean_cell(cell):
    if not isinstance(cell, str):
        return cell

    cell = cell.replace("\n", " ")

    # הסרת מילים מיותרות
    cell = re.sub(r"\bכת\b", "", cell)
    cell = re.sub(r"\bהנומ\b", "", cell)

    cell = re.sub(r"[^\d(]*\((\d+)\)[^\d)]*", r"(\1)", cell)

    # אם המחרוזת היא סוגריים בלבד (למשל (6)) – השאר כמו שהוא
    if re.fullmatch(r"\(\d+\)", cell.strip()):
        return cell.strip()

    # תיקון טקסט מהופך אם יש עברית
    cell = reverse_hebrew_words_only(cell)

    # ניקוי רווחים מיותרים
    cell = re.sub(r"\s{2,}", " ", cell).strip()

    return cell


def protect_parens(cell):
    if isinstance(cell, str) and re.fullmatch(r"\(\d+\)", cell.strip()):
        return f'="{cell}"'  # יישמר כתא טקסט מוחלט
    return cell


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.applymap(clean_cell)
    df = df.applymap(protect_parens)
    return df
