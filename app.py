from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import edge_tts
import uuid
import os

app = FastAPI(title="Hindi Edge TTS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- COMPLETE VOICE LIST (All Available Options) ---
VOICES = {
    # --- Hindi Voices (India) ---
    "hi-male": "hi-IN-MadhurNeural",       # Male (Deep/Professional)
    "hi-female": "hi-IN-SwaraNeural",      # Female (Standard News/Office)
    "hi-female-2": "hi-IN-NoopurNeural",   # Female (Fast/Sharp)

    # --- Urdu Voices (India & Pakistan) ---
    "ur-male": "ur-IN-SalmanNeural",       # Indian Urdu Male
    "ur-female": "ur-IN-GulshanNeural",    # Indian Urdu Female (New Added)
    "ur-pk-male": "ur-PK-AsadNeural",      # Pakistani Urdu Male (Heavy/Poetic)
    "ur-pk-female": "ur-PK-UzmaNeural"     # Pakistani Urdu Female (Soft Story)
}

@app.get("/")
def root():
    return {"status": "running", "engine": "Microsoft Edge TTS (Max Models)"}

@app.post("/tts")
async def tts(data: dict):
    text = data.get("text", "").strip()
    voice_key = data.get("voice", "hi-male")
    
    speed_val = int(data.get("rate", 0)) 
    pitch_val = int(data.get("pitch", 0))

    if not text:
        raise HTTPException(status_code=400, detail="Text required")

    # Default Voice
    voice = VOICES.get(voice_key, "hi-IN-MadhurNeural")
    
    rate_str = f"{speed_val:+d}%"
    pitch_str = f"{pitch_val:+d}Hz"

    out_file = f"/tmp/{uuid.uuid4()}.mp3"
    
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
        await communicate.save(out_file)
        
        if not os.path.exists(out_file):
            raise HTTPException(status_code=500, detail="Audio generation failed")

        return FileResponse(out_file, media_type="audio/mpeg", filename="audio.mp3")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
