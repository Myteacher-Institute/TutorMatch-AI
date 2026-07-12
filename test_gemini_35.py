import os
import requests

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
    key = "AQ.Ab8RN6J8GsbMgv37wPYgRRn3AlxoWhIcv_nv5-ogQOXSdmvzNQ"
    test_endpoint("gemini-3.5-flash", key)

if __name__ == "__main__":
    main()
