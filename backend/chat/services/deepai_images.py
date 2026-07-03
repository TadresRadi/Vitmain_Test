import os
import logging
from typing import Optional

import requests

from django.conf import settings

logger = logging.getLogger(__name__)


def get_deepai_token() -> Optional[str]:
    token = getattr(settings, "DEEPAI_API_TOKEN", None) or os.environ.get("DEEPAI_API_TOKEN")
    if not token:
        return None
    return token


def generate_deepai_image(*, prompt: str, output_format: str = "jpg", **kwargs) -> bytes:
    """
    DeepAI text2img:
      POST https://api.deepai.org/api/text2img

    Docs indicate:
      - header: api-key: YOUR_API_KEY
      - form field: text=<prompt>
    Response:
      200 JSON:
        { "output_url": ".../output.jpg", ... }

    This function returns raw image bytes downloaded from `output_url`.
    """
    token = get_deepai_token()
    if not token:
        raise RuntimeError("DEEPAI_API_TOKEN is not configured")

    url = "https://api.deepai.org/api/text2img"

    headers = {
        "api-key": token,
    }

    # DeepAI expects `text` field.
    data = {
        "text": prompt,
    }

    # DeepAI may support extra params depending on the model; allow passthrough.
    # output_format isn't guaranteed for DeepAI, but we keep it for API symmetry.
    data.update({k: v for k, v in kwargs.items() if v is not None})

    response = requests.post(url, headers=headers, data=data, timeout=180)

    if response.status_code != 200:
        # try json first
        try:
            payload = response.json()
        except Exception:
            payload = {"text": response.text}
        raise RuntimeError(f"DeepAI image generation failed: {response.status_code} - {payload}")

    payload = response.json()
    output_url = payload.get("output_url")
    if not output_url:
        raise RuntimeError(f"DeepAI image generation failed: missing output_url in payload: {payload}")

    img_resp = requests.get(output_url, timeout=180)
    if img_resp.status_code != 200:
        raise RuntimeError(f"DeepAI image download failed: {img_resp.status_code} - {img_resp.text[:200]}")

    return img_resp.content
