from fastapi import APIRouter, HTTPException
import traceback
from chatbot.models import ChatRequest
from auth.database import db  # Reuse MongoDB connection for storing chat history (optional)
import datetime
import sys
import sys
import urllib.parse
from email.message import Message
from email.parser import Parser

# Patch for removed cgi module
def parse_header(value):
    msg = Parser().parsestr(f"Content-Type: {value}\n")
    return msg.get_content_type(), dict(msg.items())

# Fake cgi module
sys.modules["cgi"] = type(sys)("cgi")
sys.modules["cgi"].parse_header = parse_header
from googletrans import Translator



router = APIRouter()
translator = Translator()

def translate_text(text: str, target_lang: str= "en") -> (str) :
    detected = translator.detect(text).lang
    translated = translator.translate(text, dest=target_lang).text
    return detected,translated

def translate_back(text: str, dest_lang: str) -> str :
    return translator.translate(text, dest=dest_lang).text



# Placeholder for AI model integration
def get_general_ai_response(prompt: str) -> str:
    # Replace with actual model call when provided, e.g., model.generate(prompt)
    
    return f"General AI response for prompt: '{prompt}' (Placeholder - integrate model here)"

def get_specialized_ai_response(prompt: str) -> str:
    # Replace with actual model call when provided, e.g., model.generate(prompt)
    return f"Specialized AI response for prompt: '{prompt}' (Placeholder - integrate model here)"

@router.post("/general")
async def general_chat(request: ChatRequest):
    try:

        detected_lang, translated_prompt = translate_text(request.prompt, "en")

        ai_response = f"AI response for: {translated_prompt}"

        final_response = translate_back(ai_response, detected_lang)
        response = get_general_ai_response(request.prompt)
        stored_data = {
            "input_lang": detected_lang,
            "translated_prompt": translated_prompt,
            "final_response": final_response
        }
        addition_to_response = response + f"The following is detected : {stored_data}"
        # Optionally store chat in MongoDB
        await db["chat_history"].insert_one({
            "type": "general",
            "prompt": request.prompt,
            "translated_prompt": translated_prompt,
            "final_response": final_response,
            "response": response,
            "timestamp": datetime.datetime.now()
        })
        return {"response": addition_to_response}
    except Exception as e:
        print(f"Error in /chat/general: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/specialized")
async def specialized_chat(request: ChatRequest):
    try:
        response = get_specialized_ai_response(request.prompt)
        # Optionally store chat in MongoDB
        await db["chat_history"].insert_one({
            "type": "specialized",
            "prompt": request.prompt,
            "response": response,
            "timestamp": datetime.datetime.now()
        })
        return {"response": response}
    except Exception as e:
        print(f"Error in /chat/specialized: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")