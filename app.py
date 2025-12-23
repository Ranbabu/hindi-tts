from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from piper import PiperVoice
import uuid
import os

app = FastAPI(title="Hindi Realistic TTS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VOICE_MODEL = "hi-IN-libritts-high.onnx"

# Load Piper Hindi voice
voice = PiperVoice.load(VOICE_MODEL)

@app.post("/tts")
def tts(data: dict):
    text = data.get("text", "").strip()

    if not text:
        return {"error": "Text is required"}

    out_file = f"/tmp/{uuid.uuid4()}.wav"

    with open(out_file, "wb") as f:
        voice.synthesize(text, f)

    return FileResponse(
        out_file,
        media_type="audio/wav",
        filename="speech.wav"
    )

@app.get("/")
def home():
    return {"status": "running", "engine": "Piper Hindi TTS"}
