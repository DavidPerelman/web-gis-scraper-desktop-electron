from paddleocr import PPStructure, save_structure_res
import os

# הגדרות
image_path = r"C:\Users\dpere\Documents\python-projects\web-gis-scraper-desktop-electron\backend\utils\pages\12.jpg"  # כאן תכניס תמונה של עמוד עם טבלה
output_folder = "output_structure"
output_name = "result"

# יצירת מנוע טבלאות
table_engine = PPStructure(
    table=True, ocr=True, lang="he"
)  # או "en" אם העברית לא עובדת

# הרצה
results = table_engine(image_path)

# שמירה לקובץ Excel
os.makedirs(output_folder, exist_ok=True)
save_structure_res(results, save_folder=output_folder, save_file_name=output_name)

print(f"✅ טבלה נשמרה ל־{output_folder}/{output_name}.xlsx")
