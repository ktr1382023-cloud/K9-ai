from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import torch
import soundfile as sf
import os
import uuid
import tempfile
from huggingface_hub import hf_hub_download

app = FastAPI(title="K9 AI", version="0.1.0")

# Note: The correct class for MyanmarTTS might be different. 
# We are trying a direct approach here.
model = None
load_error = None

class TTSRequest(BaseModel):
    text: str

@app.on_event("startup")
def load_model():
    global model, load_error
    print("Loading MyanmarTTS...")
    try:
        # Attempt to import directly from the package name
        from myanmartts import MyanmarTTS
        model = MyanmarTTS()
        print("Model loaded successfully!")
    except Exception as e:
        load_error = str(e)
        print(f"Error loading model: {e}")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/tts")
def generate_tts(request: TTSRequest):
    if model is None:
        raise HTTPException(status_code=503, detail=f"Error: {load_error}")
    
    try:
        temp_dir = tempfile.gettempdir()
        file_name = f"{uuid.uuid4()}.wav"
        file_path = os.path.join(temp_dir, file_name)
        
        # Generate audio
        model.speak(request.text, output_file=file_path)
        
        return FileResponse(file_path, media_type="audio/wav", filename="k9_voice.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
