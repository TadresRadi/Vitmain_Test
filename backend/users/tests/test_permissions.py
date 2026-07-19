"""
Tests for the IsAdminOrSupervisor and IsSuperAdmin permission classes.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from users.permissions import IsAdminOrSupervisor, IsSuperAdmin

User = get_user_model()

# Shared dummy password for permission tests. Not a real credential.
TEST_PASSWORD = "pass123"  # nosec B105 - test fixture, not a real credential


@pytest.mark.django_db
class TestIsAdminOrSupervisor:
    def test_super_admin_has_permission(self):
        user = User.objects.create_user(
            email="admin@example.com",
            password=TEST_PASSWORD,
            role="super_admin",
            is_email_verified=True,
        )
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        permission = IsAdminOrSupervisor()
        assert permission.has_permission(request, None) is True

    def test_supervisor_has_permission(self):
        user = User.objects.create_user(
            email="supervisor@example.com",
            password=TEST_PASSWORD,
            role="supervisor",
            is_email_verified=True,
        )
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        permission = IsAdminOrSupervisor()
        assert permission.has_permission(request, None) is True

    def test_regular_user_denied(self):
        user = User.objects.create_user(
            email="user@example.com",
            password=TEST_PASSWORD,
            role="user",
            is_email_verified=True,
        )
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        permission = IsAdminOrSupervisor()
        assert permission.has_permission(request, None) is False

    def test_anonymous_denied(self):
        from django.contrib.auth.models import AnonymousUser
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        permission = IsAdminOrSupervisor()
        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsSuperAdmin:
    def test_super_admin_has_permission(self):
        user = User.objects.create_user(
            email="admin@example.com",
            password=TEST_PASSWORD,
            role="super_admin",
            is_email_verified=True,
        )
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        permission = IsSuperAdmin()
        assert permission.has_permission(request, None) is True

    def test_supervisor_denied(self):
        user = User.objects.create_user(
            email="supervisor@example.com",
            password=TEST_PASSWORD,
            role="supervisor",
            is_email_verified=True,
        )
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        permission = IsSuperAdmin()
        assert permission.has_permission(request, None) is False

    def test_regular_user_denied(self):
        user = User.objects.create_user(
            email="user@example.com",
            password=TEST_PASSWORD,
            role="user",
            is_email_verified=True,
        )
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        permission = IsSuperAdmin()
        assert permission.has_permission(request, None) is False