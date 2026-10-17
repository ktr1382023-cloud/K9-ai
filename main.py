from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import soundfile as sf
import os
import uuid
import tempfile
from f5_myanmar_tts import MyanmarTTS

app = FastAPI(title="K9 AI", version="0.1.0")

tts = None
load_error = None

class TTSRequest(BaseModel):
    text: str

@app.on_event("startup")
def load_model():
    global tts, load_error
    print("Loading F5-Myanmar-TTS model...")
    try:
        # Auto-downloads model on first run
        tts = MyanmarTTS()
        print("Model loaded successfully!")
    except Exception as e:
        load_error = str(e)
        print(f"Error loading model: {e}")

@app.get("/")
def root():
    return {"status": "ok", "message": "K9 AI backend is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/tts")
def generate_tts(request: TTSRequest):
    if tts is None:
        detail_msg = f"Model is still loading or failed to load. Error: {load_error}" if load_error else "Model is still loading."
        raise HTTPException(status_code=503, detail=detail_msg)
    
    try:
        temp_dir = tempfile.gettempdir()
        file_name = f"{uuid.uuid4()}.wav"
        file_path = os.path.join(temp_dir, file_name)
        
        # Generate speech using F5-Myanmar-TTS
        tts.speak(request.text, output_file=file_path)
        
        return FileResponse(file_path, media_type="audio/wav", filename="k9_voice.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
