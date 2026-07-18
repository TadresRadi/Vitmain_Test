"""
Tests for the image provider registry and ABC.
"""
import pytest
from chat.services.image_provider_base import (
    ImageProvider,
    ImageProviderRegistry,
    get_image_registry,
)


class FakeProvider(ImageProvider):
    """Test provider that always succeeds."""
    name = "fake"

    def generate_image_bytes(self, prompt: str, **kwargs) -> bytes:
        return b"fake-image-bytes"


class FailingProvider(ImageProvider):
    """Test provider that is never configured."""
    name = "failing"

    def generate_image_bytes(self, prompt: str, **kwargs) -> bytes:
        return b""

    def is_configured(self) -> bool:
        return False


def test_register_and_get_provider():
    registry = ImageProviderRegistry()
    provider = FakeProvider()
    registry.register(provider)
    assert registry.get_provider("fake") is provider


def test_default_provider_selection(monkeypatch):
    monkeypatch.setenv("IMAGE_PROVIDER", "fake")
    registry = ImageProviderRegistry()
    registry.register(FakeProvider())
    assert registry.get_provider().name == "fake"


def test_unknown_provider_raises():
    registry = ImageProviderRegistry()
    with pytest.raises(ValueError, match="not registered"):
        registry.get_provider("nonexistent")


def test_unconfigured_provider_raises():
    registry = ImageProviderRegistry()
    registry.register(FailingProvider())
    with pytest.raises(ValueError, match="not configured"):
        registry.get_provider("failing")


def test_list_providers():
    registry = ImageProviderRegistry()
    registry.register(FakeProvider())
    registry.register(FailingProvider())
    providers = registry.list_providers()
    assert "fake" in providers
    assert "failing" in providers


def test_list_configured_providers():
    registry = ImageProviderRegistry()
    registry.register(FakeProvider())
    registry.register(FailingProvider())
    configured = registry.list_configured_providers()
    assert "fake" in configured
    assert "failing" not in configured


def test_pollinations_provider_is_registered():
    """The Pollinations provider should be auto-registered on import."""
    # Importing the module triggers registration
    import chat.services.pollinations_images  # noqa: F401
    registry = get_image_registry()
    assert "pollinations" in registry.list_providers()