import requests
import json

# Ensure this matches your Ollama port (default is 11434)
OLLAMA_BASE_URL = "http://localhost:11434"

def get_running_models():
    """Fetches installed models. Endpoint: /api/tags"""
    url = f"{OLLAMA_BASE_URL}/api/tags"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # The API returns a list under the 'models' key
            return [m['name'] for m in data.get('models', [])]
        else:
            print(f"Ollama Error {response.status_code}: Check if Ollama is running.")
            return ["qwen2.5-coder"] # Fallback
    except Exception as e:
        print(f"Connection Failed: {e}")
        return ["qwen2.5-coder"] # Fallback[cite: 4]

def generate_response(prompt, model_name="qwen2.5-coder", history=None):
    """Generates text. Endpoint: /api/generate"""
    if history:
        history_text = ""
        for entry in history[-5:]:
            role = "User" if entry['role'] == 'user' else "Agent"
            history_text += f"{role}: {entry['content']}\n"
        prompt = f"{history_text}\nUser: {prompt}\nAgent:"
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return {
                "model": model_name,
                "response": response.json().get("response", "")
            }
        return {"model": "ERROR", "response": f"Ollama Error: {response.status_code}"}
    except Exception as e:
        return {"model": "ERROR", "response": str(e)}