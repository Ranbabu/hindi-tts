from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import edge_tts
import uuid
import os
import asyncio

app = FastAPI(title="Hindi Edge TTS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Voice Settings ---
# Microsoft की हाई क्वालिटी आवाज़ें
VOICES = {
    "hi-male": "hi-IN-MadhurNeural",     # हिंदी पुरुष
    "hi-female": "hi-IN-SwaraNeural",    # हिंदी महिला
    "ur-male": "ur-IN-SalmanNeural",     # उर्दू पुरुष
    "ur-female": "ur-IN-GulshanNeural"   # उर्दू महिला
}

@app.get("/")
def root():
    return {"status": "running", "engine": "Microsoft Edge TTS (No Models Needed)"}

@app.post("/tts")
async def tts(data: dict):
    text = data.get("text", "").strip()
    voice_key = data.get("voice", "hi-male")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text required")

    # सही आवाज़ चुनें
    voice = VOICES.get(voice_key, "hi-IN-MadhurNeural")
    
    # आउटपुट फाइल
    out_file = f"/tmp/{uuid.uuid4()}.mp3"
    
    try:
        # Edge TTS से ऑडियो जनरेट करें
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(out_file)
        
        if not os.path.exists(out_file):
            raise HTTPException(status_code=500, detail="Audio file creation failed")

        # फाइल भेजें (Background task delete logic Render पर कभी-कभी issue करता है, 
        # इसलिए हम Render को खुद /tmp साफ़ करने देते हैं)
        return FileResponse(out_file, media_type="audio/mpeg", filename="audio.mp3")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
