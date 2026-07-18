"""
Abstract base class for image generation providers.

All image providers (Pollinations, Replicate, Stability, DeepAI) implement
this interface so they can be swapped via configuration without changing
call sites.
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class ImageProvider(ABC):
    """Abstract interface for image generation providers."""

    #: Provider name (e.g. "pollinations", "replicate"). Must be unique.
    name: str = "base"

    @abstractmethod
    def generate_image_bytes(self, prompt: str, **kwargs) -> bytes:
        """
        Generate an image from a prompt and return raw bytes.

        Args:
            prompt: The image generation prompt.
            **kwargs: Provider-specific options (model, size, etc.)

        Returns:
            Raw image bytes.

        Raises:
            RuntimeError: If generation fails.
        """
        raise NotImplementedError

    def is_configured(self) -> bool:
        """
        Check if this provider has the required credentials configured.
        Override in subclasses to check API keys, etc.
        """
        return True


class ImageProviderRegistry:
    """
    Registry for image providers. Providers register themselves by name.
    The active provider is selected via the IMAGE_PROVIDER env var
    (default: "pollinations").
    """

    def __init__(self):
        self._providers: dict[str, ImageProvider] = {}

    def register(self, provider: ImageProvider) -> None:
        """Register a provider instance."""
        if not provider.name or provider.name == "base":
            raise ValueError(f"Provider must have a non-default name: {provider}")
        self._providers[provider.name] = provider
        logger.debug(f"Registered image provider: {provider.name}")

    def get_provider(self, name: Optional[str] = None) -> ImageProvider:
        """
        Get a provider by name. If name is None, returns the provider
        selected by the IMAGE_PROVIDER env var (default: pollinations).

        Raises:
            ValueError: If the requested provider is not registered.
        """
        import os
        if name is None:
            name = os.environ.get("IMAGE_PROVIDER", "pollinations")

        if name not in self._providers:
            available = ", ".join(self._providers.keys()) or "(none)"
            raise ValueError(
                f"Image provider '{name}' not registered. "
                f"Available: {available}"
            )

        provider = self._providers[name]
        if not provider.is_configured():
            raise ValueError(
                f"Image provider '{name}' is not configured. "
                f"Check the required API keys in your .env."
            )

        return provider

    def list_providers(self) -> list[str]:
        """Return a list of registered provider names."""
        return list(self._providers.keys())

    def list_configured_providers(self) -> list[str]:
        """Return a list of providers that are configured and ready to use."""
        return [name for name, p in self._providers.items() if p.is_configured()]


# Singleton registry
_registry = ImageProviderRegistry()


def get_image_registry() -> ImageProviderRegistry:
    """Get the singleton image provider registry."""
    return _registry


def get_image_provider(name: Optional[str] = None) -> ImageProvider:
    """Convenience function: get the active image provider."""
    return _registry.get_provider(name)