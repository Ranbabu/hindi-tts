from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI(title="Hindi TTS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPER_BIN = os.path.join(BASE_DIR, "piper", "piper")
MODELS_DIR = os.path.join(BASE_DIR, "models")

VOICE_MAP = {
    "hi-male": "hi-male.onnx",
    "ur-male": "hi-male.onnx",
    "hi-female": "hi-female.onnx"
}
DEFAULT_MODEL = "hi-male.onnx"

@app.get("/")
def root():
    return {"status": "running", "engine": "Piper TTS"}

@app.post("/tts")
def tts(data: dict):
    text = data.get("text", "").strip()
    voice = data.get("voice", "hi-male")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text required")

    model_name = VOICE_MAP.get(voice, DEFAULT_MODEL)
    model_path = os.path.join(MODELS_DIR, model_name)
    config_path = f"{model_path}.json"

    # Safety check
    if not os.path.exists(model_path) or not os.path.exists(config_path):
        raise HTTPException(status_code=500, detail="Model files missing on server. Check logs.")

    out_file = f"/tmp/{uuid.uuid4()}.wav"
    
    cmd = [PIPER_BIN, "--model", model_path, "--config", config_path, "--output_file", out_file]
    
    try:
        proc = subprocess.run(cmd, input=text.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise Exception(proc.stderr.decode())
            
        return FileResponse(out_file, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
