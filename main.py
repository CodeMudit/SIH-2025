from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from chatbot.routes import router as chatbot_router
from weather.routes import router as weather_router
from image_analysis.routes import router as image_router
from micro_calculator.routes import router as micro_router
from fastapi.staticfiles import StaticFiles
from news.routes import router as news_router


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Serve React build
app.mount("/assets", StaticFiles(directory="frontend_dist/assets"), name="assets")

@app.get("/favicon.ico")
async def favicon():
    fav = os.path.join("frontend_dist", "favicon.ico")
    if os.path.exists(fav):
        return FileResponse(fav)
    return FileResponse(os.path.join("frontend_dist", "assets", "favicon.ico"))

@app.get("/")
async def root():
    return FileResponse(os.path.join("frontend_dist", "index.html"))

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    requested = os.path.join("frontend_dist", full_path)
    if os.path.isfile(requested):
        return FileResponse(requested)
    return FileResponse(os.path.join("frontend_dist", "index.html"))



app.mount("/uploadvoices", StaticFiles(directory="uploadvoices"), name="uploadvoices")
app.mount("/uploadimages", StaticFiles(directory="uploadimages"), name="uploadimages")

# Add CORS middleware for frontend integration (optional, adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chatbot_router, prefix="/chat", tags=["chat"])
app.include_router(weather_router, prefix="/weather", tags=["weather"])
app.include_router(image_router, prefix="/image-analysis", tags=["image-analysis"])
app.include_router(micro_router, prefix="/micro-calculator", tags=["calculator"])
# Health check endpoint

@app.get("/")
async def root():
    return {"message": "Farmer Chatbot Backend is running"}