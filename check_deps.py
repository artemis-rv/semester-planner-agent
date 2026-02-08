import os
import shutil
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

def check_dependencies():
    print("--- System Dependency Check ---")
    
    # 1. Tesseract
    tesseract_exists = shutil.which("tesseract")
    if tesseract_exists:
        print(f"[OK] Tesseract found at: {tesseract_exists}")
    else:
        print("[FAIL] Tesseract NOT found in PATH. OCR for images will fail.")

    # 2. Poppler
    poppler_exists = shutil.which("pdftoppm")
    if poppler_exists:
        print(f"[OK] Poppler found at: {poppler_exists}")
    else:
        print("[FAIL] Poppler NOT found in PATH. PDF processing will fail.")

    # 3. Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        print(f"[OK] GEMINI_API_KEY found (starts with {api_key[:4]}...)")
    else:
        print("[FAIL] GEMINI_API_KEY is missing/invalid in .env.")

    print("\n--- Project Module Integrity Check ---")
    
    modules_to_check = [
        ("planner.ingestion.cleaner", "import re; from planner.ingestion.cleaner import SyllabusCleaner"),
        ("planner.ai.extractor", "from planner.ai.extractor import Syllabusextractor"),
    ]

    for mod_name, test_cmd in modules_to_check:
        try:
            # Add current dir to path
            sys.path.append(os.getcwd())
            exec(test_cmd)
            print(f"[OK] Module '{mod_name}' imports correctly.")
        except Exception as e:
            print(f"[FAIL] Module '{mod_name}' failed: {e}")

if __name__ == "__main__":
    check_dependencies()
