import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_flash():
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        response = model.generate_content("Say hello")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_flash()
