from fastapi import FastAPI, BackgroundTasks
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

PIPER_BIN = "./piper/piper"
MODELS_DIR = "./models"

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.get("/")
def root():
    return {"status": "running", "engine": "Piper TTS"}

@app.post("/tts")
async def tts(data: dict, background_tasks: BackgroundTasks):
    text = data.get("text", "").strip()
    voice_type = data.get("voice", "hi-male")

    if not text:
        return {"error": "Text required"}

    # मॉडल का चुनाव
    model_name = "hi.onnx"
    if voice_type == "hi-female":
        model_name = "hi_female.onnx"
    elif voice_type == "ur-male":
        model_name = "ur_male.onnx"

    model_path = os.path.join(MODELS_DIR, model_name)
    # अगर फाइल नहीं मिली तो डिफॉल्ट hi.onnx इस्तेमाल करें
    if not os.path.exists(model_path):
        model_path = os.path.join(MODELS_DIR, "hi.onnx")
    
    config_path = model_path + ".json"
    out_file = f"/tmp/{uuid.uuid4()}.wav"

    cmd = [
        PIPER_BIN,
        "--model", model_path,
        "--config", config_path,
        "--output_file", out_file
    ]

    try:
        process = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120 # बढ़ा हुआ टाइमआउट
        )

        if process.returncode != 0:
            return {"error": process.stderr.decode()}

        background_tasks.add_task(remove_file, out_file)
        return FileResponse(path=out_file, media_type="audio/wav")

    except Exception as e:
        return {"error": str(e)}
