import os
import logging
from typing import Optional

import requests

from django.conf import settings

logger = logging.getLogger(__name__)


def get_stability_token() -> Optional[str]:
    token = getattr(settings, "STABILITY_API_TOKEN", None) or os.environ.get("STABILITY_API_TOKEN")
    if not token:
        return None
    return token


def generate_stability_image(
    *,
    prompt: str,
    output_format: str = "webp",
    model: str = "stable-image/generate/ultra",
    **kwargs,
) -> bytes:
    """Generate an image via Stability AI and return raw image bytes.

    Endpoint (docs):
      https://api.stability.ai/v2beta/stable-image/generate/ultra

    We intentionally keep this minimal and return bytes so the caller can persist.
    """

    token = get_stability_token()
    if not token:
        raise RuntimeError("STABILITY_API_TOKEN is not configured")

    url = f"https://api.stability.ai/v2beta/{model}"

    headers = {
        "authorization": f"Bearer {token}",
        "accept": "image/*",
    }

    # Stability expects multipart form-data in many examples, but plain form fields also work.
    # We follow the documented approach using `data`.
    data = {
        "prompt": prompt,
        "output_format": output_format,
    }
    # allow callers to pass through additional knobs if the API supports them
    data.update({k: v for k, v in kwargs.items() if v is not None})

    # Example in docs uses files={"none": ''}.
    # We keep compatibility with that pattern.
    # Stability docs show using `files={"none": ""}`.
    # Some responses may include non-JSON bodies; we handle errors robustly in caller.
    response = requests.post(url, headers=headers, data=data, files={"none": ""}, timeout=180)


    if response.status_code == 200:
        return response.content

    # Best-effort error payload
    try:
        payload = response.json()
    except Exception:
        payload = {"text": response.text}

    raise RuntimeError(f"Stability image generation failed: {response.status_code} - {payload}")

