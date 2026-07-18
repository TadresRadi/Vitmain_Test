import logging
import os
from typing import Optional
from urllib.parse import quote
from chat.services.image_provider_base import ImageProvider, get_image_registry

import requests

from django.conf import settings

logger = logging.getLogger(__name__)


def get_pollinations_token() -> Optional[str]:
    token = getattr(settings, "POLLINATIONS_API_KEY", None) or os.environ.get(
        "POLLINATIONS_API_KEY"
    )
    if not token:
        return None
    return token.strip()


def generate_pollinations_image_bytes(
    *,
    prompt: str,
    model: str = "flux",
    output_ext: str = "jpg",
) -> bytes:
    """Generate an image using Pollinations.

    Pollinations docs:
      - https://gen.pollinations.ai/image/<prompt>?model=flux

    If your plan requires auth, we send:
      Authorization: Bearer <POLLINATIONS_API_KEY>

    Returns raw image bytes.
    """
    token = get_pollinations_token()
    if not token:
        raise RuntimeError(
            "POLLINATIONS_API_KEY is not configured. Set POLLINATIONS_API_KEY in .env."
        )

    # URL encode prompt for path usage
    prompt_path = quote(prompt, safe="")
    url = f"https://gen.pollinations.ai/image/{prompt_path}?model={model}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "image/*",
    }

    resp = requests.get(url, headers=headers, timeout=180)
    if resp.status_code == 200:
        return resp.content

    # best-effort payload
    try:
        payload = resp.json()
    except Exception:
        payload = {"text": resp.text[:500]}

    raise RuntimeError(f"Pollinations image generation failed: {resp.status_code} - {payload}")

class PollinationsImageProvider(ImageProvider):
    """Pollinations image provider implementation."""
    name = "pollinations"

    def generate_image_bytes(self, prompt: str, **kwargs) -> bytes:
        model = kwargs.get("model", "flux")
        output_ext = kwargs.get("output_ext", "jpg")
        return generate_pollinations_image_bytes(
            prompt=prompt,
            model=model,
            output_ext=output_ext,
        )

    def is_configured(self) -> bool:
        return get_pollinations_token() is not None


# Register with the global registry
get_image_registry().register(PollinationsImageProvider())
