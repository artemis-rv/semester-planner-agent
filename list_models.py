import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        with open("models_debug.txt", "w") as f:
            f.write("GEMINI_API_KEY not found in .env\n")
        return

    genai.configure(api_key=api_key)
    
    try:
        models = list(genai.list_models())
        with open("models_debug.txt", "w") as f:
            f.write(f"Total models found: {len(models)}\n")
            for m in models:
                f.write(f"Name: {m.name}, Methods: {m.supported_generation_methods}\n")
    except Exception as e:
        with open("models_debug.txt", "w") as f:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    list_models()
