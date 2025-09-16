from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

class ChatRequest(BaseModel):
    prompt: str


class DashboardResponse(BaseModel):
    name: str
    location: dict | None = None
    weather: dict | None = None
    news: list[dict] | None = None
    market_prices: list[dict] | None = None

class VoiceChatRequest(BaseModel):
    audio: UploadFile  # Audio file (e.g., WAV/MP3)
    lang: Optional[str] = None  # Optional hint; STT auto-detects