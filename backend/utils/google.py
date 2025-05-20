import base64
import requests
from test import load_ocr_text, save_ocr_text
from pdf2image import convert_from_path
import os
from typing import List


def ocr_google_vision(image_path, api_key):
    # קריאה של התמונה והמרה ל־base64
    with open(image_path, "rb") as image_file:
        content = base64.b64encode(image_file.read()).decode("utf-8")

    # בקשת POST
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "requests": [
            {
                "image": {"content": content},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                "imageContext": {"languageHints": ["he"]},
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    # print(response.json())

    try:
        text = result["responses"][0]["fullTextAnnotation"]["text"]
        return text
    except KeyError:
        print("⚠️ OCR failed or no text found.")
        return ""


def convert_pdf_to_images(pdf_path: str, output_folder: str) -> List[str]:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = convert_from_path(pdf_path)
    image_paths = []

    for i, image in enumerate(images, start=1):
        image_path = os.path.join(output_folder, f"page_{i}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths


def save_ocr_per_page(image_paths: List[str], api_key: str):
    for img_path in image_paths:
        page_num = os.path.splitext(os.path.basename(img_path))[0].split("_")[1]
        txt_path = img_path.replace(".png", ".txt")

        text = ocr_google_vision(img_path, api_key)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"📄 נשמר: {txt_path}")


pdf_file = r"C:\Users\dpere\Downloads\101-0206748_הוראות התכנית - מאושרות - חתום_תוכנית מאושרת.pdf"
output_folder = "pdf_images-101-0206748"

API_KEY = "AIzaSyDTpyE7-7K96na5D0_C0niae4-KE4GvzTY"

# המרה לתמונות
image_paths = convert_pdf_to_images(pdf_file, output_folder)

# הרצת OCR ושמירה
save_ocr_per_page(image_paths, API_KEY)


USE_CACHE = True  # שנה ל־False כדי להריץ OCR אמיתי

if USE_CACHE:
    text = load_ocr_text()
else:
    text = ocr_google_vision("page_13.png", API_KEY)
    save_ocr_text(text)
