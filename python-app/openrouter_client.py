import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY not found in .env")

URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "openrouter/free",
    "messages": [
        {"role": "user", "content": "Hello! This is a test message. Just say 'it works' and nothing else."}
    ],
    "max_tokens": 20,
}

try:
    response = requests.post(URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Connection successful!")
    print("Response:", data["choices"][0]["message"]["content"])
except requests.exceptions.RequestException as e:
    print("Request failed:", e)