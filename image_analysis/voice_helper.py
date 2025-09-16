import uuid
import os
from google.cloud import texttospeech
import re

UPLOAD_VOICE_DIR = "uploadvoices"
os.makedirs(UPLOAD_VOICE_DIR, exist_ok=True)

def clean_label_for_voice(label_text: str) -> str:
    """Clean label text for natural speech (e.g., 'Tomato__Late_blight' -> 'Tomato Late Blight')."""
    text = label_text.replace("_", " ").replace(",", " ")
    text = " ".join(text.split())  # Remove extra spaces
    return text

def generate_voice(
    summary_text: str, 
    lang: str = "hi", 
    use_ssml: bool = False,  # Optional SSML for pronunciation hints
    custom_rate: float = None,  # Optional speaking rate override
    custom_pitch: float = None   # Optional pitch override
) -> str:
    """Generate human-like voice audio using Google Cloud TTS.
    
    Backward-compatible: Defaults to plain text (no SSML) and standard config.
    For enhanced pronunciation (e.g., Hindi/Punjabi), set use_ssml=True.
    """
    voice_filename = f"{uuid.uuid4().hex}.mp3"
    file_path = os.path.join(UPLOAD_VOICE_DIR, voice_filename)

    # Map app's lang codes to Google Cloud TTS voice settings
    voice_map = {
        'hi': {'language_code': 'hi-IN', 'name': 'hi-IN-Wavenet-A', 'ssml_gender': 'FEMALE'},
        'hinglish': {'language_code': 'hi-IN', 'name': 'hi-IN-Wavenet-A', 'ssml_gender': 'FEMALE'},
        'en': {'language_code': 'en-IN', 'name': 'en-IN-Wavenet-C', 'ssml_gender': 'FEMALE'},
        'pa': {'language_code': 'pa-IN', 'name': 'pa-IN-Wavenet-A', 'ssml_gender': 'FEMALE'}
        # Add more as needed
    }
    voice_config = voice_map.get(lang, voice_map['hi'])  # Default to Hindi for Hinglish

    try:
        # Clean the text (always, for compatibility)
        cleaned_text = re.sub(r'\\n', ' ', summary_text)  # Replace \n with space
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize multiple spaces
        cleaned_text = re.sub(r'[^\w\s.,!?]', '', cleaned_text)  # Keep only letters, numbers, and basic punctuation
        cleaned_text = cleaned_text.strip()  # Remove leading/trailing spaces

        # SSML enhancement (optional)
        input_text = cleaned_text
        if use_ssml:
            ssml_text = f"<speak>{cleaned_text}</speak>"
            # Add phonetic hints for specific words (language-specific)
            if lang in ['hi', 'hinglish']:
                ssml_text = ssml_text.replace("Diplocarpon", "<phoneme alphabet='ipa' ph='dɪploʊˈkɑːrpən'>Diplocarpon</phoneme>")
                # Add more: e.g., ssml_text = ssml_text.replace("patton", "<phoneme alphabet='ipa' ph='pət̪ən'>patton</phoneme>")
            elif lang == 'pa':
                ssml_text = ssml_text.replace("ਸੰਭਾਲ", "<phoneme alphabet='ipa' ph='səmˈbʱaːl'>ਸੰਭਾਲ</phoneme>")
                # Add more Punjabi words as needed
            input_text = ssml_text  # Use SSML if enabled

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(ssml=input_text if use_ssml else cleaned_text)  # SSML or plain

        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config['language_code'],
            name=voice_config['name'],
            ssml_gender=texttospeech.SsmlVoiceGender[voice_config['ssml_gender']]
        )

        # Audio config with optional overrides
        base_rate = 0.95 if lang in ['hi', 'hinglish', 'pa'] else 1.0
        base_pitch = -0.5 if lang in ['hi', 'hinglish', 'pa'] else 0.0
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=custom_rate or base_rate,  # Use custom if provided, else base
            pitch=custom_pitch or base_pitch        # Use custom if provided, else base
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(file_path, 'wb') as out:
            out.write(response.audio_content)
        print(f"✅ Voice file generated: {file_path} (SSML: {use_ssml})")
        return voice_filename
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        return None