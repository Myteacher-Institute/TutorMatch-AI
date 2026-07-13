import os
import requests
from dotenv import load_dotenv

def test_endpoint(model, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": "Say hello in one word!"}]}]
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing model '{model}'...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    if not key:
        print("GEMINI_API_KEY is not configured.")
        return
    test_endpoint(model, key)

if __name__ == "__main__":
    main()
