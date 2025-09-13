from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from chatbot.routes import router as chatbot_router
from weather.routes import router as weather_router
from image_analysis.routes import router as image_router
app = FastAPI()

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
# Health check endpoint

@app.get("/")
async def root():
    return {"message": "Farmer Chatbot Backend is running"}
