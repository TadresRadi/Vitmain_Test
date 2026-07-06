import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(email="test@example.com", password="password123")

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def rf():
    return RequestFactory()

@pytest.fixture
def anon_request(rf):
    req = rf.get("/")
    req.user = AnonymousUser()
    return req