
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from myanmar_tts import MyanmarTTS
import soundfile as sf
import os
import uuid
import tempfile

app = FastAPI(title="K9 AI", version="0.2.0")

model = None
load_error = None


class TTSRequest(BaseModel):
    text: str


@app.on_event("startup")
def load_model():
    global model, load_error

    try:
        print("Loading K9 Myanmar voice model...")
        model = MyanmarTTS(device="cpu")
        print("K9 model loaded successfully!")

    except Exception as e:
        load_error = str(e)
        print(f"Model loading error: {e}")


@app.get("/")
def root():
    return {"status": "K9 AI Voice is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/tts")
def generate_tts(request: TTSRequest):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model loading error: {load_error}"
        )

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="စာသားထည့်ပေးပါ"
        )

    try:
        audio = model.tts(
            request.text,
            solver="euler",
            step=12,
            cfg=3.0
        )

        file_path = os.path.join(
            tempfile.gettempdir(),
            f"{uuid.uuid4()}.wav"
        )

        sf.write(file_path, audio, 44100)

        return FileResponse(
            file_path,
            media_type="audio/wav",
            filename="k9_voice.wav"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
