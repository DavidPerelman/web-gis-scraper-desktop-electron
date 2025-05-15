import zipfile
from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import geopandas as gpd
from pathlib import Path


from services.iplan_fetcher import IplanFetcher

router = APIRouter()

import warnings  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)


@router.post("/upload-polygon")
async def upload_polygon(file: UploadFile = File(...)):
    allowed_extensions = (".zip", ".geojson", ".json", ".shp")
    if not file.filename.endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file format")

    upload_path = Path("temp_uploads")
    upload_path.mkdir(parents=True, exist_ok=True)
    file_location = upload_path / file.filename

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if file.filename.endswith(".zip"):
            extract_dir = upload_path / file.filename.replace(".zip", "")
            extract_dir.mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(str(file_location), str(extract_dir))
            required_exts = {".shp", ".shx", ".dbf"}
            with zipfile.ZipFile(file_location, "r") as zf:
                uploaded_exts = {Path(name).suffix.lower() for name in zf.namelist()}

            if not required_exts.issubset(uploaded_exts):
                raise HTTPException(
                    status_code=400,
                    detail="ZIP must include .shp, .shx, and .dbf files",
                )
            shp_files = list(extract_dir.glob("*.shp"))
            if not shp_files:
                raise Exception("No .shp file found inside the ZIP archive.")
            gdf = gpd.read_file(shp_files[0])
        else:
            gdf = gpd.read_file(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

    # העשרת תכניות
    fetcher = IplanFetcher(gdf)
    plans = await fetcher.run()

    return plans
