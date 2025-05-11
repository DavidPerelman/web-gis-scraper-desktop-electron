from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from typing import Optional

from backend.app.services.polygon_loader import upload_polygon

router = APIRouter()

# הגדרת גודל מקסימלי לקובץ - 20MB
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes


@router.post(
    "/upload-polygon",
    summary="העלאת קובץ גיאוגרפי",
    description="נתיב לקבלת קובץ גיאוגרפי (GeoJSON, Shapefile ב־ZIP או JSON) ומחזורו לפוליגון",
    response_description="פוליגון בפורמט GeoJSON",
)
async def upload_polygon_route(
    file: UploadFile = File(...),
):
    """
    נתיב לקבלת קובץ גיאוגרפי ומחזורו לפוליגון בפורמט GeoJSON.

    Parameters:
    -----------
    file : UploadFile
        קובץ גיאוגרפי (GeoJSON, Shapefile ב־ZIP, או JSON)

    Returns:
    --------
    JSONResponse
        פוליגון בפורמט GeoJSON

    Raises:
    -------
    HTTPException
        - 400: פורמט קובץ לא תקין או נתונים לא תקינים
        - 413: גודל קובץ חורג מהמותר
        - 500: שגיאה כללית בעיבוד
    """
    # בדיקת גודל קובץ
    file_size = 0
    chunk_size = 1024  # 1KB chunks

    # קריאת חלק מהקובץ לבדיקת גודל
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            await file.seek(0)  # החזרת מצביע הקובץ להתחלה
            raise HTTPException(
                status_code=413,
                detail=f"גודל הקובץ חורג מהמותר. הגודל המקסימלי הוא {MAX_FILE_SIZE / (1024 * 1024):.1f}MB",
            )

    # החזרת מצביע הקובץ להתחלה
    await file.seek(0)

    try:
        # קריאה לפונקציה upload_polygon להחזיר GeoDataFrame
        gdf = await upload_polygon(file)

        # המרת GeoDataFrame ל־GeoJSON כמחרוזת
        geojson_str = gdf.to_json()

        # המרת המחרוזת ל־dict כדי להחזיר כ־JSON תקני
        geojson_dict = json.loads(geojson_str)

        # החזרת GeoJSON כ־JSONResponse
        return JSONResponse(content=geojson_dict)

    except HTTPException as e:
        # העברת שגיאות HTTPException כמו שהן
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": f"שגיאה בעיבוד הקובץ: {str(e)}"}
        )
