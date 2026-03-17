import requests
from core.utils import load_key

def azure_tts(text: str, save_path: str) -> None:
    url = "https://api.302.ai/cognitiveservices/v1"
    
    API_KEY = load_key("azure_tts.api_key")
    voice = load_key("azure_tts.voice")
    
    payload = f"""<speak version='1.0' xml:lang='zh-CN'><voice name='{voice}'>{text}</voice></speak>"""
    headers = {
       'Authorization': f'Bearer {API_KEY}',
       'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm',
       'Content-Type': 'application/ssml+xml'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if not response.ok:
        error_text = response.text.strip().replace("\n", " ")[:300]
        raise RuntimeError(f"Azure TTS request failed: HTTP {response.status_code}, body={error_text}")

    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith(("audio/", "application/octet-stream")):
        error_text = response.text.strip().replace("\n", " ")[:300]
        raise RuntimeError(f"Azure TTS returned non-audio content: Content-Type={content_type}, body={error_text}")

    if not response.content.startswith((b'RIFF', b'ID3')):
        snippet = response.content[:80]
        raise RuntimeError(f"Azure TTS returned unexpected audio header: {snippet!r}")

    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"Audio saved to {save_path}")

if __name__ == "__main__":
    azure_tts("Hi! Welcome to VideoLingo!", "test.wav")