#!/usr/bin/env bash

echo "----------- STARTING FRESH SETUP -----------"

# 1. पुरानी खराब फाइल्स को साफ़ करें (ताकि Error न आए)
echo "Cleaning up old corrupted files..."
rm -rf models
rm -rf piper

# 2. PIPER डाउनलोड करें
echo "Downloading Piper..."
wget -O piper.tar.gz https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
tar -xvf piper.tar.gz
rm piper.tar.gz

# 3. MODELS डाउनलोड करें (Curl का उपयोग करेंगे जो ज्यादा सुरक्षित है)
echo "Downloading Hindi Models..."
mkdir -p models

# (A) Hindi Male
echo "Downloading Male Voice..."
curl -L -o models/hi-male.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/pratham/hgh/hi_IN-pratham-hgh.onnx"
curl -L -o models/hi-male.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/pratham/hgh/hi_IN-pratham-hgh.onnx.json"

# (B) Hindi Female
echo "Downloading Female Voice..."
curl -L -o models/hi-female.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/alma/medium/hi_IN-alma-medium.onnx"
curl -L -o models/hi-female.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/alma/medium/hi_IN-alma-medium.onnx.json"

# 4. Permissions सेट करें
chmod +x ./piper/piper

# 5. चेक करें कि फाइल्स सही से डाउनलोड हुई या नहीं
if [ ! -s "models/hi-male.onnx.json" ]; then
  echo "ERROR: Model JSON file is empty! Download failed."
  exit 1
fi

echo "Setup Complete. Starting Server..."
uvicorn app:app --host 0.0.0.0 --port $PORT
