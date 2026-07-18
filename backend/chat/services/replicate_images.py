import os
import logging
from typing import Optional

import replicate

from django.conf import settings

logger = logging.getLogger(__name__)


def get_replicate_client():
    """Return a Replicate client using REPLICATE_API_TOKEN.

    Token is read from environment (loaded by django settings via load_dotenv).
    """
    token = getattr(settings, "REPLICATE_API_TOKEN", None) or os.environ.get(
        "REPLICATE_API_TOKEN"
    )
    if not token:
        return None
    # replicate expects either token or api_token depending on version;
    # `replicate.Client(api_token=...)` is the most common.
    return replicate.Client(api_token=token)


def generate_image(prompt: str, model: str, version: Optional[str] = None, **kwargs) -> str:
    """Generate an image and return a URL (or best-effort string).

    This is intentionally generic; callers should pass model/version and any
    extra input params required by that model.
    """
    client = get_replicate_client()
    if not client:
        raise RuntimeError("REPLICATE_API_TOKEN is not configured")

    # Replicate API: versions can be specified as model:version
    model_ref = model
    if version:
        model_ref = f"{model}:{version}"

    # Replicate image models (google/imagen-4) typically accept these keys.
    # We set safe defaults and allow callers to override via kwargs.
    input_payload = {
        "prompt": prompt,
        "aspect_ratio": kwargs.pop("aspect_ratio", "16:9"),
        "safety_filter_level": kwargs.pop(
            "safety_filter_level", "block_medium_and_above"
        ),
    }
    input_payload.update(kwargs)


    prediction = client.run(model_ref, input=input_payload)

    # `prediction` can be a dict-like streaming result depending on client/version.
    # Best-effort: try to locate an URL.
    if isinstance(prediction, str):
        return prediction

    if isinstance(prediction, dict):
        for key in ["output", "image", "url", "result"]:
            if key in prediction and prediction[key]:
                value = prediction[key]
                if isinstance(value, list) and value:
                    return str(value[0])
                return str(value)

    return str(prediction)

from chat.services.image_provider_base import ImageProvider, get_image_registry

class ReplicateImageProvider(ImageProvider):
    name = "replicate"

    def generate_image_bytes(self, prompt: str, **kwargs) -> bytes:
        # Call the existing module-level function
        from chat.services.replicate_images import generate_replicate_image_bytes
        return generate_replicate_image_bytes(prompt=prompt, **kwargs)

    def is_configured(self) -> bool:
        import os
        return bool(os.environ.get("REPLICATE_API_TOKEN", "").strip())


get_image_registry().register(ReplicateImageProvider())

