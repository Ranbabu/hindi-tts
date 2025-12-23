from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import torch, soundfile as sf, os, tarfile, urllib.request
from fairseq.checkpoint_utils import load_model_ensemble_and_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = "model"
MODEL_PT = "model/hin/model.pt"
MODEL_URL = "https://dl.fbaipublicfiles.com/mms/tts/hin.tar.gz"

def prepare_model():
    if not os.path.exists(MODEL_PT):
        os.makedirs("model", exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, "hin.tar.gz")
        with tarfile.open("hin.tar.gz") as tar:
            tar.extractall("model")

prepare_model()

models, cfg, task = load_model_ensemble_and_task([MODEL_PT])
model = models[0]
model.eval()

@app.post("/tts")
def tts(data: dict):
    text = data.get("text", "")
    if not text.strip():
        return {"error": "No text"}

    with torch.no_grad():
        wav = model.infer(text, sample_rate=16000)

    sf.write("output.wav", wav, 16000)
    return FileResponse("output.wav", media_type="audio/wav")
