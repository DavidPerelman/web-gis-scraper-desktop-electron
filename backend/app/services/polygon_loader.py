from pathlib import Path
import os
import shutil
import zipfile
import tempfile
from typing import List
from fastapi import File, UploadFile, HTTPException as FastAPIHTTPException
import geopandas as gpd


async def upload_polygon(file: UploadFile = File(...)):
    """
    מקבלת קובץ ומעבדת אותו לפוליגון גיאוגרפי.

    תומכת בפורמטים: GeoJSON, JSON, וקבצי Shapefile (באמצעות ZIP).

    Parameters:
    -----------
    file : UploadFile
        קובץ להעלאה, יכול להיות ZIP עם shapefile או קובץ GeoJSON/JSON

    Returns:
    --------
    GeoDataFrame
        אובייקט GeoDataFrame עם הפוליגונים שנטענו

    Raises:
    -------
    HTTPException
        במקרה של שגיאה בקובץ או בעיבוד
    """
    # בדיקת סיומת קובץ
    allowed_extensions = (".zip", ".geojson", ".json", ".shp")
    file_ext = os.path.splitext(file.filename.lower())[1]

    if file_ext not in allowed_extensions:
        raise FastAPIHTTPException(
            status_code=400,
            detail=f"פורמט קובץ לא תקין. פורמטים מורשים: {', '.join(allowed_extensions)}",
        )

    # שימוש בתיקייה זמנית במקום תיקייה קבועה
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        file_location = temp_dir_path / file.filename

        # שמירת הקובץ המועלה
        try:
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise FastAPIHTTPException(
                status_code=500, detail=f"שגיאה בשמירת הקובץ: {str(e)}"
            )
        finally:
            # החזרת מצביע הקובץ להתחלה למקרה שנרצה להשתמש בו שוב
            await file.seek(0)

        try:
            # טיפול בקובץ ZIP (Shapefile)
            if file_ext == ".zip":
                gdf = _process_zip_file(file_location, temp_dir_path)
            # טיפול בקבצי GeoJSON/JSON/SHP
            else:
                gdf = gpd.read_file(file_location)

                # וידוא שהקובץ מכיל נתונים גיאומטריים
                if gdf.empty or not gdf.geometry.any():
                    raise FastAPIHTTPException(
                        status_code=400,
                        detail="הקובץ אינו מכיל נתונים גיאומטריים תקינים",
                    )

            # בדיקה שלא מדובר בקובץ ריק
            if gdf.empty:
                raise FastAPIHTTPException(
                    status_code=400, detail="הקובץ שהועלה אינו מכיל נתונים"
                )

            return gdf

        except Exception as e:
            # לא צריך לנקות את הקבצים הזמניים כי התיקייה הזמנית תימחק אוטומטית
            if isinstance(e, FastAPIHTTPException):
                raise e
            raise FastAPIHTTPException(
                status_code=500, detail=f"שגיאה בקריאת הקובץ: {str(e)}"
            )


def _process_zip_file(zip_path: Path, extract_dir: Path) -> gpd.GeoDataFrame:
    """
    מעבד קובץ ZIP שאמור להכיל קבצי Shapefile.

    Parameters:
    -----------
    zip_path : Path
        נתיב לקובץ ה-ZIP
    extract_dir : Path
        נתיב לתיקייה לחילוץ הקבצים

    Returns:
    --------
    gpd.GeoDataFrame
        אובייקט GeoDataFrame עם הנתונים שנטענו

    Raises:
    -------
    HTTPException
        במקרה של שגיאה בקובץ ZIP או בקבצי ה-shapefile
    """
    # בדיקה שזה קובץ ZIP תקין
    if not zipfile.is_zipfile(zip_path):
        raise FastAPIHTTPException(status_code=400, detail="קובץ ה-ZIP אינו תקין")

    # בדיקת תכולת קובץ ה-ZIP
    shapefile_exts: List[str] = []
    shp_files: List[str] = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        # מונע Path Traversal attacks
        for file_info in zf.infolist():
            # דילוג על תיקיות ועל קבצים נסתרים
            if file_info.filename.endswith("/") or os.path.basename(
                file_info.filename
            ).startswith("."):
                continue

            file_ext = os.path.splitext(file_info.filename.lower())[1]
            if file_ext in (".shp", ".shx", ".dbf", ".prj"):
                shapefile_exts.append(file_ext)

            if file_ext == ".shp":
                shp_files.append(file_info.filename)

        # בדיקה שיש את כל הקבצים הדרושים
        required_exts = {".shp", ".shx", ".dbf"}
        if not all(ext in shapefile_exts for ext in required_exts):
            raise FastAPIHTTPException(
                status_code=400, detail="קובץ ה-ZIP חייב לכלול קבצי .shp, .shx, ו-.dbf"
            )

        if not shp_files:
            raise FastAPIHTTPException(
                status_code=400, detail="לא נמצא קובץ .shp בארכיון ה-ZIP"
            )

        # חילוץ רק הקבצים הדרושים
        extract_subdir = extract_dir / "shapefile_data"
        extract_subdir.mkdir(exist_ok=True)

        # מחלץ את כל הקבצים הדרושים לקובץ ה-shapefile הראשון שנמצא
        main_shp = shp_files[0]
        base_name = os.path.splitext(os.path.basename(main_shp))[0]
        base_path = os.path.dirname(main_shp)

        for file_info in zf.infolist():
            current_file = file_info.filename
            current_basename = os.path.basename(current_file)

            # אם זה קובץ שקשור ל-shapefile הראשון, חלץ אותו
            if (
                os.path.dirname(current_file) == base_path
                and os.path.splitext(current_basename)[0] == base_name
            ):
                zf.extract(file_info, extract_subdir)

    # טעינת קובץ ה-shapefile
    shp_path = extract_subdir / os.path.basename(shp_files[0])
    if not shp_path.exists():
        raise FastAPIHTTPException(
            status_code=500, detail="שגיאה בחילוץ קבצי ה-Shapefile"
        )

    try:
        gdf = gpd.read_file(shp_path)
        return gdf
    except Exception as e:
        raise FastAPIHTTPException(
            status_code=500, detail=f"שגיאה בטעינת קובץ ה-Shapefile: {str(e)}"
        )
