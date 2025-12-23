import os
import requests
import tarfile
import shutil

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIPER_DIR = os.path.join(BASE_DIR, "piper")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Piper Linux URL
PIPER_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz"

# Valid Model URLs (HuggingFace)
MODELS = {
    "hi-male": {
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/pratham/hgh/hi_IN-pratham-hgh.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/pratham/hgh/hi_IN-pratham-hgh.onnx.json"
    },
    "hi-female": {
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/alma/medium/hi_IN-alma-medium.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/alma/medium/hi_IN-alma-medium.onnx.json"
    }
}

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        print(f"✅ File exists: {dest_path}")
        return

    print(f"⬇️ Downloading {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Check for 404/500 errors
        
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Saved to {dest_path}")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path) # Delete corrupt file

def setup_piper():
    if not os.path.exists(os.path.join(PIPER_DIR, "piper")):
        print("⚙️ Setting up Piper...")
        os.makedirs(PIPER_DIR, exist_ok=True)
        tar_path = "piper.tar.gz"
        download_file(PIPER_URL, tar_path)
        
        print("📦 Extracting Piper...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=BASE_DIR) # Extracts to ./piper/
        
        os.remove(tar_path)
        # Permissions
        piper_bin = os.path.join(PIPER_DIR, "piper")
        if os.path.exists(piper_bin):
            os.chmod(piper_bin, 0o755)
    else:
        print("✅ Piper is ready.")

def setup_models():
    os.makedirs(MODELS_DIR, exist_ok=True)
    for name, urls in MODELS.items():
        print(f"🔍 Checking voice: {name}")
        onnx_path = os.path.join(MODELS_DIR, f"{name}.onnx")
        json_path = os.path.join(MODELS_DIR, f"{name}.onnx.json")
        
        download_file(urls["onnx"], onnx_path)
        download_file(urls["json"], json_path)

        # Integrity Check: Read first byte of JSON to ensure it's not "Error" or HTML
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read(10).strip()
                if not content.startswith("{"):
                    print(f"⚠️ CORRUPT JSON detected for {name}. Deleting...")
                    os.remove(json_path)
                    os.remove(onnx_path)
        except Exception:
            pass

if __name__ == "__main__":
    setup_piper()
    setup_models()
    print("🚀 Setup Complete!")
