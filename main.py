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

model = None
ref_audio_path = None
load_error = None

class TTSRequest(BaseModel):
    text: str

@app.on_event("startup")
def load_model():
    global model, ref_audio_path, load_error
    print("Loading MyanmarTTS...")
    try:
        from api import StableTTSAPI
        from burmese import burmese_to_ipa2
        
        model_path = hf_hub_download("freococo/MyanmarTTS", "model_fp16.pt")
        vocos_path = hf_hub_download("freococo/MyanmarTTS", "vocos.pt")
        ref_audio_path = hf_hub_download("freococo/MyanmarTTS", "samples/sample_0.wav")
        
        model = StableTTSAPI(model_path, vocos_path, "vocos").to("cpu")
        model.g2p_mapping["burmese"] = burmese_to_ipa2
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
        audio, _ = model.inference(
            request.text, 
            ref_audio_path, 
            "burmese", 
            step=32, 
            solver="dopri5", 
            cfg=3.0
        )
        
        temp_dir = tempfile.gettempdir()
        file_name = f"{uuid.uuid4()}.wav"
        file_path = os.path.join(temp_dir, file_name)
        
        sf.write(file_path, audio.squeeze(0).cpu().numpy(), 44100)
        
        return FileResponse(file_path, media_type="audio/wav", filename="k9_voice.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
