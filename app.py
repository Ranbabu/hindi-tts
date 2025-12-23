from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI(title="Hindi TTS API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPER_BIN = os.path.join(BASE_DIR, "piper", "piper")
MODELS_DIR = os.path.join(BASE_DIR, "models")

def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except:
        pass

# Voice Mapping
VOICE_MAP = {
    "hi-male": "hi-male.onnx",
    "ur-male": "hi-male.onnx",
    "hi-female": "hi-female.onnx"
}
DEFAULT_MODEL = "hi-male.onnx"

@app.get("/")
def root():
    return {
        "status": "running", 
        "engine": "Piper TTS", 
        "piper_path": PIPER_BIN,
        "piper_exists": os.path.exists(PIPER_BIN)
    }

@app.post("/tts")
async def tts(data: dict, background_tasks: BackgroundTasks):
    text = data.get("text", "").strip()
    voice_type = data.get("voice", "hi-male")

    if not text:
        raise HTTPException(status_code=400, detail="Text is empty")

    # Model Selection
    model_filename = VOICE_MAP.get(voice_type, DEFAULT_MODEL)
    model_path = os.path.join(MODELS_DIR, model_filename)
    config_path = f"{model_path}.json"

    # Check if files exist
    if not os.path.exists(PIPER_BIN):
        raise HTTPException(status_code=500, detail="Server Error: Piper binary missing. Check start.sh logs.")
    
    if not os.path.exists(model_path):
        # Fallback to whatever model is available
        available_models = [f for f in os.listdir(MODELS_DIR) if f.endswith(".onnx")]
        if available_models:
            model_path = os.path.join(MODELS_DIR, available_models[0])
            config_path = f"{model_path}.json"
        else:
            raise HTTPException(status_code=500, detail="Server Error: No models found. Still downloading?")

    out_file = f"/tmp/{uuid.uuid4()}.wav"

    cmd = [
        PIPER_BIN,
        "--model", model_path,
        "--config", config_path,
        "--output_file", out_file
    ]

    try:
        # Run Piper
        process = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if process.returncode != 0:
            error_msg = process.stderr.decode()
            print(f"Piper Error: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Piper Failed: {error_msg}")

        if not os.path.exists(out_file) or os.path.getsize(out_file) == 0:
             raise HTTPException(status_code=500, detail="Audio file was not created or is empty.")

        background_tasks.add_task(remove_file, out_file)
        return FileResponse(path=out_file, media_type="audio/wav")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
