import os
from google.cloud import texttospeech

# Debug: Print the env var and file existence
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if credentials_path and os.path.exists(credentials_path):
    print(f"✅ JSON file exists at: {credentials_path}")
    file_size = os.path.getsize(credentials_path)
    print(f"File size: {file_size} bytes (should be >1000)")
else:
    print(f"❌ JSON file NOT found or env var not set!")
    if credentials_path:
        print(f"Path checked: {credentials_path}")
    exit(1)  # Stop if file missing

try:
    client = texttospeech.TextToSpeechClient()
    print("✅ TTS Client created successfully! Authentication works.")
except Exception as e:
    print(f"❌ Error creating client: {type(e).__name__}: {str(e)}")
    import traceback
    print(traceback.format_exc())