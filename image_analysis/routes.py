from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.database import db
import traceback
import datetime
import shutil
import uuid
from image_analysis.prediction import model_predict  # Import ML function
import os

UPLOAD_DIR = "uploadimages"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Redundant but safe

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/analyze")
async def analyze_image_endpoint(request: Request, file: UploadFile = File(...)):
    try:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Only JPEG or PNG images are supported")

        filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
        image_path = os.path.join(UPLOAD_DIR, filename)

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        analysis_result = model_predict(image_path)

        await db["image_analyses"].insert_one({
            "filename": filename,
            "full_path": image_path,
            "analysis_result": analysis_result,
            "timestamp": datetime.datetime.now()
        })

        return {
            "filename": filename,
            "image_url": f"/uploadimages/{filename}",
            "analysis_result": analysis_result,
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        print(f"Error in /analyze: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/dashboard", response_class=HTMLResponse)
async def image_analysis_dashboard(request: Request):
    try:
        analyses = await db["image_analyses"].find().sort("timestamp", -1).to_list(length=10)
        analyses = [
            {
                "filename": analysis["filename"],
                "image_url": f"/uploadimages/{analysis['filename']}",
                "analysis_result": analysis["analysis_result"],
                "timestamp": str(analysis["timestamp"])
            }
            for analysis in analyses
        ]
        return templates.TemplateResponse("image_dashboard.html", {"request": request, "analyses": analyses})
    except Exception as e:
        print(f"Error in /dashboard: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")