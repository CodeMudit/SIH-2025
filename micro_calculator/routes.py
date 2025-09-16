# routes.py (in micro_calculator directory)
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from micro_calculator.crop_advisor import CropAdvisor

router = APIRouter()

# Templates
templates = Jinja2Templates(directory="templates")

advisor = CropAdvisor()

# Translations
translations = {
    "en": {
        "title": "🌱 Crop Drop",
        "subtitle": "Get AI-powered irrigation and fertilizer recommendations",
        "crop_label": "Select Crop:",
        "stage_label": "Growth Stage:",
        "state_label": "State:",
        "location_label": "Location Coordinates:",
        "latitude_placeholder": "Latitude",
        "longitude_placeholder": "Longitude",
        "calculate_btn": "Get Recommendation",
        "loading_text": "🔄 Calculating... Getting NASA data...",
        "irrigation_title": "💧 Irrigation Advice",
        "fertilizer_title": "🌾 Fertilizer Advice",
        "et0_label": "Reference ET₀:",
        "kc_label": "Crop Coefficient (Kc):",
        "etc_label": "Crop ETc:",
        "rainfall_label": "Rainfall:",
        "irrigation_need_label": "Irrigation Needed:",
        "skip_irrigation": "→ Skip irrigation this week",
        "apply_irrigation": "→ Apply {} mm water this week",
        "soil_values_label": "Soil Nutrients:",
        "urea_label": "Urea:",
        "dap_label": "DAP:",
        "mop_label": "MOP:",
        "kg_ha": "kg/ha",
        "based_on_location": "Based on your location's soil conditions",
        "split_basal": "Basal (Sowing): 40%",
        "split_vegetative": "Vegetative: 30%",
        "split_reproductive": "Reproductive: 30%"
    },
    "hi": {
        "title": "🌱 स्मार्ट फसल सलाहकार",
        "subtitle": "AI-संचालित सिंचाई और उर्वरक सिफारिशें प्राप्त करें",
        "crop_label": "फसल चुनें:",
        "stage_label": "विकास अवस्था:",
        "state_label": "राज्य:",
        "location_label": "स्थान निर्देशांक:",
        "latitude_placeholder": "अक्षांश",
        "longitude_placeholder": "देशांतर",
        "calculate_btn": "सिफारिश प्राप्त करें",
        "loading_text": "🔄 गणना चल रही है... NASA डेटा प्राप्त हो रहा है...",
        "irrigation_title": "💧 सिंचाई सलाह",
        "fertilizer_title": "🌾 उर्वरक सलाह",
        "et0_label": "संदर्भ ET₀:",
        "kc_label": "फसल गुणांक (Kc):",
        "etc_label": "फसल ETc:",
        "rainfall_label": "वर्षा:",
        "irrigation_need_label": "सिंचाई आवश्यक:",
        "skip_irrigation": "→ इस सप्ताह सिंचाई छोड़ें",
        "apply_irrigation": "→ इस सप्ताह {} mm पानी लगाएं",
        "soil_values_label": "मिट्टी पोषक तत्व:",
        "urea_label": "यूरिया:",
        "dap_label": "डीएपी:",
        "mop_label": "एमओपी:",
        "kg_ha": "kg/ha",
        "based_on_location": "आपके location की मिट्टी की स्थिति के आधार पर",
        "split_basal": "बेसल (बुआई): 40%",
        "split_vegetative": "वानस्पतिक: 30%",
        "split_reproductive": "प्रजनन: 30%"
    }
}

# Pydantic Model
class AdviceRequest(BaseModel):
    crop_type: str
    growth_stage: str
    state: str
    lang: str = "en"

# Routes
@router.get("/", response_class=HTMLResponse)
async def home(request: Request, lang: str = "en"):
    lang = lang if lang in translations else "en"
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "lang": lang,
            "t": translations[lang],
            "translations": translations
        }
    )

@router.post("/get_advice")
async def get_advice(req: AdviceRequest):
    try:
        advice = advisor.generate_advice(
            req.crop_type.lower(),
            req.growth_stage.lower(),
            req.state.lower()
        )
        return JSONResponse({"success": True, "advice": advice, "lang": req.lang})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})