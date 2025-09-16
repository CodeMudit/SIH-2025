from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from weather.services import fetch_weather, fetch_weather_by_coords
import requests
import feedparser
from auth.database import users_collection
from chatbot.models import DashboardResponse

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


@router.get("/dashboard/{phone}", response_model=DashboardResponse)
async def dashboard(phone: str):
    # Load user
    user = await users_collection.find_one({"phone": phone})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    name = user.get("name")
    location = user.get("location") or {}
    lat = location.get("lat")
    lon = location.get("lon")

    # Weather by coordinates
    weather = None
    if lat is not None and lon is not None:
        weather = fetch_weather_by_coords(lat, lon)

    # News: use Google News RSS with geo keywords
    news_items = []
    try:
        # Construct a query favoring agriculture/crop topics
        query = "agriculture OR crop OR farming"
        region = f"{location.get('district','')} {location.get('state','')}".strip()
        q = f"{query} {region}".strip()
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(q)}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            news_items.append({
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published"),
            })
    except Exception:
        news_items = []

    # Market prices: placeholder using Agmarknet-like structure (no key used)
    market_prices = []
    try:
        # Placeholder static or pseudo source. Replace with actual API if available.
        # For demo, fetch a public JSON sample or construct a simple list
        market_prices = [
            {"commodity": "Wheat", "state": location.get("state"), "price_per_qtl": 2150},
            {"commodity": "Rice", "state": location.get("state"), "price_per_qtl": 2400},
            {"commodity": "Maize", "state": location.get("state"), "price_per_qtl": 1900},
        ]
    except Exception:
        market_prices = []

    return DashboardResponse(
        name=name,
        location=location,
        weather=weather,
        news=news_items,
        market_prices=market_prices,
    )