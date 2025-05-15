import uvicorn
from main import app

import os
import sys

# איתור נתיב unpacked של PyInstaller (בתוך _MEIPASS או תיקיית ההרצה)
app_dir = getattr(sys, '_MEIPASS', os.path.abspath("."))

# הוספה ל־sys.path – כדי שפייתון יוכל לייבא חבילות
sys.path.insert(0, os.path.join(app_dir, "fiona"))
sys.path.insert(0, os.path.join(app_dir, "geopandas"))
sys.path.insert(0, os.path.join(app_dir, "shapely"))
sys.path.insert(0, os.path.join(app_dir, "pyproj"))

# הוספה ל־PATH – כדי לאפשר טעינת DLLים
os.environ["PATH"] = os.pathsep.join([
    os.environ.get("PATH", ""),
    os.path.join(app_dir, "fiona.libs"),
    os.path.join(app_dir, "Shapely.libs"),
    os.path.join(app_dir, "pyproj.libs"),
])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)