"""
system_ai - First-time setup wizard
Downloads the required model if not present
"""
import os
import sys
import json
from pathlib import Path

MODEL_URL = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
MODEL_FILENAME = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"

def get_config_path():
    """Find config.json relative to install or cwd"""
    candidates = [
        Path.cwd() / "config" / "config.json",
        Path(__file__).parent.parent / "config" / "config.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

def get_model_dir():
    config_path = get_config_path()
    if config_path:
        with open(config_path) as f:
            config = json.load(f)
        model_path = Path(config.get("local_model_path", "models/" + MODEL_FILENAME))
        if not model_path.is_absolute():
            model_path = config_path.parent.parent / model_path
        return model_path
    return Path.home() / ".system_ai" / "models" / MODEL_FILENAME

def download_model():
    dest = get_model_dir()
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        print(f"Model already exists: {dest}")
        return str(dest)

    print(f"Downloading model to {dest}")
    print("This is ~2GB - please wait...")

    try:
        import requests
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  {pct:.1f}%", end="", flush=True)

        print(f"\nDone. Model saved to: {dest}")
        return str(dest)

    except Exception as e:
        print(f"Download failed: {e}")
        print(f"Manually download from:\n  {MODEL_URL}")
        print(f"And place it at:\n  {dest}")
        sys.exit(1)

def main():
    print("=== system_ai Setup ===")
    download_model()
    print("\nSetup complete. Run: system_ai")

if __name__ == "__main__":
    main()
