from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import shutil

app = FastAPI(title="Hindi TTS API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# रास्ते (Paths) सेट करना
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPER_BIN = os.path.join(BASE_DIR, "piper", "piper")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# फाइल डिलीट करने का फंक्शन (Cleanup)
def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Error deleting file: {e}")

# वॉयस मैपिंग (Frontend से जो नाम आएगा, उसे सही फाइल से जोड़ना)
VOICE_MAP = {
    "hi-male": "hi-male.onnx",
    "ur-male": "hi-male.onnx",   # उर्दू के लिए भी हिंदी मेल मॉडल (फिलहाल)
    "hi-female": "hi-female.onnx"
}
DEFAULT_MODEL = "hi-male.onnx"

@app.get("/")
def root():
    # चेक करें कि Piper डाउनलोड हुआ या नहीं
    piper_status = "Installed" if os.path.exists(PIPER_BIN) else "Missing (Check Logs)"
    return {
        "status": "running", 
        "engine": "Piper TTS", 
        "piper_binary": piper_status
    }

@app.post("/tts")
async def tts(data: dict, background_tasks: BackgroundTasks):
    text = data.get("text", "").strip()
    voice_type = data.get("voice", "hi-male")

    if not text:
        return {"error": "Text required"}

    # सही मॉडल फाइल चुनें
    model_filename = VOICE_MAP.get(voice_type, DEFAULT_MODEL)
    model_path = os.path.join(MODELS_DIR, model_filename)
    config_path = f"{model_path}.json"

    # अगर स्पेसिफिक मॉडल नहीं मिला, तो जो भी मौजूद है उसे यूज़ करें (Crash से बचने के लिए)
    if not os.path.exists(model_path):
        print(f"Requested model {model_filename} not found, checking fallback...")
        fallback_path = os.path.join(MODELS_DIR, DEFAULT_MODEL)
        if os.path.exists(fallback_path):
            model_path = fallback_path
            config_path = f"{model_path}.json"
        else:
            return {"error": "Server is still downloading models. Please wait 1 minute and try again."}

    # आउटपुट फाइल का नाम
    out_file = f"/tmp/{uuid.uuid4()}.wav"

    cmd = [
        PIPER_BIN,
        "--model", model_path,
        "--config", config_path,
        "--output_file", out_file
    ]

    try:
        # Piper कमांड रन करें
        process = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if process.returncode != 0:
            return {"error": f"Piper Error: {process.stderr.decode()}"}

        # बैकग्राउंड में फाइल डिलीट करने का टास्क सेट करें और फाइल भेजें
        background_tasks.add_task(remove_file, out_file)
        return FileResponse(path=out_file, media_type="audio/wav")

    except Exception as e:
        return {"error": str(e)}
