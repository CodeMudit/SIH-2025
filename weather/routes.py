from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from weather.services import fetch_weather

router = APIRouter()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@router.get("/{location}")
async def get_weather(location: str):
    data = fetch_weather(location)
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

@router.get("/dashboard", response_class=HTMLResponse)
async def weather_dashboard(request: Request, location: str = "London"):
    weather_data = fetch_weather(location)
    if "error" in weather_data:
        weather_data = {"location": location, "error": weather_data["error"]}
    return templates.TemplateResponse("dashboard.html", {"request": request, "weather": weather_data})