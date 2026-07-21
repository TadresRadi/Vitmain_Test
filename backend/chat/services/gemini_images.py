import os
import requests
import base64
import logging
from chat.services.image_provider_base import ImageProvider, get_image_registry

logger = logging.getLogger(__name__)

class GeminiImageProvider(ImageProvider):
    """Google Gemini image generation provider (Nano Banana)."""
    name = "gemini"

    def generate_image_bytes(self, prompt: str, **kwargs) -> bytes:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate an image: {prompt}"
                }]
            }],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini image generation failed: {resp.status_code} - {resp.text[:500]}")

        data = resp.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                image_b64 = part["inlineData"]["data"]
                return base64.b64decode(image_b64)

        raise RuntimeError("Gemini returned no image data")

    def is_configured(self) -> bool:
        return bool(os.environ.get("GEMINI_API_KEY", "").strip())

get_image_registry().register(GeminiImageProvider())