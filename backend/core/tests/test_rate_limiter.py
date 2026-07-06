import pytest
from core.rate_limit import RateLimiter, RateLimitConfig
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

@pytest.mark.django_db
def test_rate_limiter_ip_blocking(monkeypatch):
    rf = RequestFactory()
    req = rf.get("/auth/login", REMOTE_ADDR="1.2.3.4")
    req.user = AnonymousUser()

    # ensure small limit for testing
    monkeypatch.setitem(RateLimitConfig.ENDPOINTS, 'auth_login', '2/m')
    # first request: allowed
    limited, retry = RateLimiter.is_rate_limited(req, 'auth_login')
    assert not limited
    # second request: allowed
    limited, retry = RateLimiter.is_rate_limited(req, 'auth_login')
    assert not limited
    # third request: should be limited
    limited, retry = RateLimiter.is_rate_limited(req, 'auth_login')
    assert limited
    assert isinstance(retry, int)

@pytest.mark.django_db
def test_rate_limiter_user_identification(user):
    rf = RequestFactory()
    req = rf.get("/api/some", REMOTE_ADDR="1.2.3.5")
    req.user = user
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setitem(RateLimitConfig.ENDPOINTS, 'api_default', '3/m')
        # calls for authenticated user
        assert not RateLimiter.is_rate_limited(req, 'api_default')[0]
        assert not RateLimiter.is_rate_limited(req, 'api_default')[0]
        assert not RateLimiter.is_rate_limited(req, 'api_default')[0]
        limited, _ = RateLimiter.is_rate_limited(req, 'api_default')
        assert limited is True
    finally:
        monkeypatch.undo()