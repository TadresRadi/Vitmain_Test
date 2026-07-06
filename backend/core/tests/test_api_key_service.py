import pytest
from django.utils import timezone
from core.api_key_service import get_api_key_service
from django.contrib.auth import get_user_model
from core.api_key_models import APIKey

User = get_user_model()

@pytest.mark.django_db
def test_create_and_validate_api_key(user):
    svc = get_api_key_service()
    raw_key, api_key = svc.create_api_key(user=user, name="test-key", scope="read")
    assert raw_key.startswith("vitmain_")
    assert isinstance(api_key, APIKey)
    # The DB should store only hash & prefix
    assert api_key.key_prefix == raw_key[:32]
    assert api_key.key_hash != raw_key
    # validate
    validated = svc.validate_key(raw_key)
    assert validated is not None
    assert validated.id == api_key.id

@pytest.mark.django_db
def test_rotate_and_revoke_api_key(user):
    svc = get_api_key_service()
    raw_key, api_key = svc.create_api_key(user=user, name="rotate-key", scope="read")
    new_raw, new_api = svc.rotate_key(api_key, user)
    assert new_raw.startswith("vitmain_")
    # old key should be marked inactive
    api_key.refresh_from_db()
    assert api_key.status in ("inactive", "revoked")
    # revoke new key
    result = svc.revoke_key(new_api, user, reason="test")
    assert result is True
    new_api.refresh_from_db()
    assert new_api.status == "revoked"