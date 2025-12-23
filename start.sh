#!/usr/bin/env bash

echo "----------- STARTING SETUP -----------"

# 1. PIPER सेटअप (अगर मौजूद नहीं है)
if [ ! -f "./piper/piper" ]; then
    echo "Piper missing. Downloading Linux version..."
    # Piper का Linux वर्ज़न डाउनलोड करें
    wget -O piper.tar.gz https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
    
    echo "Extracting Piper..."
    tar -xvf piper.tar.gz
    rm piper.tar.gz
else
    echo "Piper is already installed."
fi

# 2. MODELS सेटअप
mkdir -p models

# (A) Hindi Male Model (Pratham)
if [ ! -f "./models/hi-male.onnx" ]; then
    echo "Downloading Hindi Male Model..."
    wget -O models/hi-male.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/pratham/hgh/hi_IN-pratham-hgh.onnx
    wget -O models/hi-male.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/pratham/hgh/hi_IN-pratham-hgh.onnx.json
fi

# (B) Hindi Female Model (Alma)
if [ ! -f "./models/hi-female.onnx" ]; then
    echo "Downloading Hindi Female Model..."
    wget -O models/hi-female.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/alma/medium/hi_IN-alma-medium.onnx
    wget -O models/hi-female.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/alma/medium/hi_IN-alma-medium.onnx.json
fi

echo "All Models Ready."

# 3. Permissions देना
chmod +x ./piper/piper

# 4. सर्वर स्टार्ट करना
echo "Starting FastAPI Server..."
uvicorn app:app --host 0.0.0.0 --port $PORT
