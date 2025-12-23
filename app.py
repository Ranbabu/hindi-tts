from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import subprocess, uuid, os

app = FastAPI(title="Hindi TTS API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PIPER_BIN = "./piper/piper"
MODEL_PATH = "./models/hi.onnx"
CONFIG_PATH = "./models/hi.onnx.json"


@app.get("/")
def root():
    return {
        "status": "running",
        "engine": "Piper TTS",
        "language": "Hindi / Urdu",
    }


@app.post("/tts")
def tts(data: dict):
    text = data.get("text", "").strip()
    if not text:
        return {"error": "Text required"}

    out_file = f"/tmp/{uuid.uuid4()}.wav"

    cmd = [
        PIPER_BIN,
        "--model", MODEL_PATH,
        "--config", CONFIG_PATH,
        "--output_file", out_file
    ]

    process = subprocess.run(
        cmd,
        input=text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if process.returncode != 0:
        return {"error": process.stderr.decode()}

    with open(out_file, "rb") as f:
        audio = f.read()

    return Response(content=audio, media_type="audio/wav")
