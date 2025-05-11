from fastapi import APIRouter, UploadFile, File

from backend.app.services.polygon_loader import upload_polygon

router = APIRouter()


@router.post("/upload-polygon")
async def upload(file: UploadFile = File(...)):
    return await upload_polygon(file)
