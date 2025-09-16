from fastapi import APIRouter, HTTPException, UploadFile, File
import traceback
from chatbot.models import ChatRequest, VoiceChatRequest
from auth.database import db  # Reuse MongoDB for chat history
import datetime
import shutil
import uuid
import os
from chatbot.app import get_gemini_response, transcribe_audio
from image_analysis.voice_helper import generate_voice  # Reuse TTS from image analysis

router = APIRouter()

UPLOAD_AUDIO_DIR = "uploadaudio"
os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True)

def get_general_ai_response(prompt: str) -> str:
    """General AI response using Gemini (non-agri fallback if needed)."""
    return get_gemini_response(prompt)  # Direct call, no wrapping

async def save_chat_to_db(chat_data: dict):
    """Async helper to save chat to MongoDB."""
    try:
        await db["chat_history"].insert_one(chat_data)
        print("✅ Chat saved to DB")
    except Exception as e:
        print(f"❌ DB save error: {e}")

@router.post("/general")
async def general_chat(request: ChatRequest):
    try:
        response = get_general_ai_response(request.prompt)
        # Store in MongoDB (simplified, no translation fields)
        await db["chat_history"].insert_one({
            "type": "general",
            "prompt": request.prompt,
            "response": response,
            "timestamp": datetime.datetime.now()
        })
        return {"response": response}
    except Exception as e:
        print(f"Error in /chat/general: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/voice_chat")
async def voice_chat(audio: UploadFile = File(..., description="Audio file (WAV/MP3, <60s)")):
    try:
        if audio.content_type not in ["audio/wav", "audio/mpeg", "audio/mp3"]:
            raise HTTPException(status_code=400, detail="Only WAV/MP3 audio supported")

        # Save uploaded audio temporarily
        filename = f"temp_audio_{uuid.uuid4().hex}.{audio.filename.split('.')[-1]}"
        audio_path = os.path.join(UPLOAD_AUDIO_DIR, filename)
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # Transcribe audio to text + detect language
        with open(audio_path, "rb") as f:
            audio_content = f.read()
        transcript, detected_lang = transcribe_audio(audio_content)

        if "failed" in transcript.lower():
            raise HTTPException(status_code=400, detail="Audio transcription failed. Please try clearer speech.")

        print(f"🔍 Transcribed: '{transcript}' (Detected lang: {detected_lang})")

        # Get Gemini response in detected language
        response = get_general_ai_response(transcript)  # Use general endpoint logic

        # Generate voice response in detected language with SSML for better pronunciation
        voice_filename = generate_voice(
            response,
            lang=detected_lang.split('-')[0],
            use_ssml=True,
            custom_rate=0.95
        )

        # Save to DB
        chat_data = {
            "type": "voice_chat",
            "transcript": transcript,
            "detected_lang": detected_lang,
            "response": response,
            "voice_file": voice_filename,
            "timestamp": datetime.datetime.now()
        }
        await save_chat_to_db(chat_data)

        # Clean up temp audio
        os.remove(audio_path)

        return {
            "transcript": transcript,
            "detected_language": detected_lang,
            "response_text": response,
            "voice_url": f"/uploadvoices/{voice_filename}" if voice_filename else None,
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        print(f"Error in /voice_chat: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")