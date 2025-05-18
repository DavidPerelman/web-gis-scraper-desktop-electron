import pdfplumber


def is_quantitative_table_start(page, header_keywords):
    table = page.extract_table()
    if not table:
        return False

    headers = table[0]
    normalized_headers = [
        h.replace("\n", " ") if isinstance(h, str) else "" for h in headers
    ]

    matches = {kw: [h for h in normalized_headers if kw in h] for kw in header_keywords}

    for kw, matched in matches.items():
        if matched:
            return True
        else:
            pass


def is_table_end(page):
    text = page.extract_text()
    if not text:
        return True  # עמוד ריק מסיים טבלה

    end_text = ".עצומה בצמה טירשתב ןיבו תינכתה תוארוהב ןיב ,תורחא תויללכ תוארוה לע ,הריתס לש הרקמב ,רבוג וז הלבטב רומאה"

    if end_text in text:
        return True


def extract_quantitative_table(pdf_path, header_keywords):
    table_pages = []

    table_started = False
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):

            if not table_started:
                if is_quantitative_table_start(page, header_keywords):
                    table_pages.append(page_num + 1)
                    table_started = True
                else:
                    continue  # continue to the next page

            if table_started:
                if is_table_end(page):
                    table_started = False
                    table_pages.append(page_num + 1)
                    break  # סוף הטבלה
    return table_pages


if __name__ == "__main__":
    # pdf_path = r"C:\Users\dpere\Documents\python-projects\web-gis-scraper-desktop-electron\backend\101-0925198_תדפיס הוראות התכנית_חתום לאישור_1.pdf"
    pdf_path = r"C:\Users\dpere\Documents\python-projects\web-gis-scraper-desktop-electron\backend\101-0135004_תדפיס הוראות התכנית_חתום לאישור_1.pdf"

    header_keywords = [
        "םוקמ / ןיינב",
        "שרגמ לדוג",
        "הינב יחטש",
        'ד"חי רפסמ',
    ]  # מילות מפתח רלוונטיות לטבלאות כמותיות
    table = extract_quantitative_table(pdf_path, header_keywords)
    print(table)
