"""
Tests for admin views (user management, role changes, overview, audit logs).

These tests verify:
- Permission checks (only super_admin / supervisor can access)
- Destructive operation safety (can't delete self, can't delete super admin)
- Role change validation
- Audit logging of admin actions
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def super_admin(db):
    return User.objects.create_user(
        email="admin@example.com",
        password="adminpass123",
        role="super_admin",
        is_staff=True,
        is_superuser=True,
        is_email_verified=True,
    )


@pytest.fixture
def supervisor(db):
    return User.objects.create_user(
        email="supervisor@example.com",
        password="superpass123",
        role="supervisor",
        is_staff=True,
        is_email_verified=True,
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email="user@example.com",
        password="userpass123",
        role="user",
        is_email_verified=True,
    )


@pytest.fixture
def admin_client(super_admin):
    """APIClient authenticated as super_admin."""
    client = APIClient()
    client.force_authenticate(user=super_admin)
    return client


@pytest.fixture
def supervisor_client(supervisor):
    """APIClient authenticated as supervisor."""
    client = APIClient()
    client.force_authenticate(user=supervisor)
    return client


@pytest.fixture
def user_client(regular_user):
    """APIClient authenticated as regular user."""
    client = APIClient()
    client.force_authenticate(user=regular_user)
    return client


# ============================================================================
# AdminAuthLoginView tests
# ============================================================================

@pytest.mark.django_db
class TestAdminAuthLogin:
    def test_admin_can_login_with_correct_credentials(self):
        User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            role="super_admin",
            is_staff=True,
            is_superuser=True,
            is_email_verified=True,
        )
        client = APIClient()
        resp = client.post(
            "/api/admin/auth/login",
            {"email": "admin@example.com", "password": "adminpass123"},
            format="json",
        )
        assert resp.status_code == 200
        assert "access_token" in resp.data
        assert resp.data["user"]["role"] == "super_admin"

    def test_regular_user_cannot_login_via_admin_portal(self):
        User.objects.create_user(
            email="user@example.com",
            password="userpass123",
            role="user",
            is_email_verified=True,
        )
        client = APIClient()
        resp = client.post(
            "/api/admin/auth/login",
            {"email": "user@example.com", "password": "userpass123"},
            format="json",
        )
        assert resp.status_code == 403

    def test_login_with_wrong_password_returns_401(self):
        User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            role="super_admin",
            is_staff=True,
            is_superuser=True,
            is_email_verified=True,
        )
        client = APIClient()
        resp = client.post(
            "/api/admin/auth/login",
            {"email": "admin@example.com", "password": "wrongpass"},
            format="json",
        )
        assert resp.status_code == 401

    def test_login_with_missing_fields_returns_400(self):
        client = APIClient()
        resp = client.post(
            "/api/admin/auth/login",
            {"email": ""},
            format="json",
        )
        assert resp.status_code == 400

    def test_supervisor_can_login_via_admin_portal(self):
        User.objects.create_user(
            email="super@example.com",
            password="superpass123",
            role="supervisor",
            is_staff=True,
            is_email_verified=True,
        )
        client = APIClient()
        resp = client.post(
            "/api/admin/auth/login",
            {"email": "super@example.com", "password": "superpass123"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["user"]["role"] == "supervisor"


# ============================================================================
# AdminAuthProfileView tests
# ============================================================================

@pytest.mark.django_db
class TestAdminAuthProfile:
    def test_admin_can_get_own_profile(self, admin_client, super_admin):
        resp = admin_client.get("/api/admin/auth/profile")
        assert resp.status_code == 200
        assert resp.data["email"] == super_admin.email
        assert resp.data["role"] == "super_admin"

    def test_regular_user_cannot_access_admin_profile(self, user_client):
        resp = user_client.get("/api/admin/auth/profile")
        assert resp.status_code == 403


# ============================================================================
# AdminOverviewView tests
# ============================================================================

@pytest.mark.django_db
class TestAdminOverview:
    def test_admin_can_get_overview(self, admin_client):
        resp = admin_client.get("/api/admin/overview")
        assert resp.status_code == 200
        assert "total_users" in resp.data
        assert "subscribed_users" in resp.data
        assert "total_payments" in resp.data
        assert "total_posts" in resp.data
        assert "total_images" in resp.data
        assert "user_growth" in resp.data
        assert "subscription_distribution" in resp.data

    def test_regular_user_cannot_get_overview(self, user_client):
        resp = user_client.get("/api/admin/overview")
        assert resp.status_code == 403

    def test_supervisor_can_get_overview(self, supervisor_client):
        resp = supervisor_client.get("/api/admin/overview")
        assert resp.status_code == 200


# ============================================================================
# AdminUserListView tests (GET + DELETE)
# ============================================================================

@pytest.mark.django_db
class TestAdminUserList:
    def test_admin_can_list_users(self, admin_client, regular_user):
        resp = admin_client.get("/api/admin/users")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)
        # Should include at least the regular_user and the admin
        assert len(resp.data) >= 2

    def test_regular_user_cannot_list_users(self, user_client):
        resp = user_client.get("/api/admin/users")
        assert resp.status_code == 403

    def test_admin_can_delete_user(self, admin_client, regular_user):
        resp = admin_client.delete(f"/api/admin/users/{regular_user.id}")
        assert resp.status_code == 200
        assert not User.objects.filter(id=regular_user.id).exists()

    def test_admin_cannot_delete_self(self, admin_client, super_admin):
        resp = admin_client.delete(f"/api/admin/users/{super_admin.id}")
        assert resp.status_code == 403
        assert User.objects.filter(id=super_admin.id).exists()

    def test_admin_cannot_delete_super_admin(self, admin_client, db):
        other_admin = User.objects.create_user(
            email="other-admin@example.com",
            password="pass123",
            role="super_admin",
            is_staff=True,
            is_superuser=True,
            is_email_verified=True,
        )
        resp = admin_client.delete(f"/api/admin/users/{other_admin.id}")
        assert resp.status_code == 403
        assert User.objects.filter(id=other_admin.id).exists()

    def test_supervisor_cannot_delete_user(self, supervisor_client, regular_user):
        """Only super_admin can delete users — supervisor gets 403."""
        resp = supervisor_client.delete(f"/api/admin/users/{regular_user.id}")
        assert resp.status_code == 403
        assert User.objects.filter(id=regular_user.id).exists()

    def test_delete_nonexistent_user_returns_404(self, admin_client):
        import uuid
        resp = admin_client.delete(f"/api/admin/users/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_delete_invalid_uuid_returns_404(self, admin_client):
        """Non-UUID strings are rejected by the URL router (uuid:user_id),
        returning 404 before the view is reached."""
        resp = admin_client.delete("/api/admin/users/not-a-uuid")
        assert resp.status_code == 404


# ============================================================================
# AdminUserRoleView tests
# ============================================================================

@pytest.mark.django_db
class TestAdminUserRole:
    def test_super_admin_can_change_user_role(self, admin_client, regular_user):
        resp = admin_client.put(
            f"/api/admin/users/{regular_user.id}/role",
            {"role": "supervisor"},
            format="json",
        )
        assert resp.status_code == 200
        regular_user.refresh_from_db()
        assert regular_user.role == "supervisor"
        assert regular_user.is_staff is True

    def test_supervisor_cannot_change_roles(self, supervisor_client, regular_user):
        resp = supervisor_client.put(
            f"/api/admin/users/{regular_user.id}/role",
            {"role": "supervisor"},
            format="json",
        )
        assert resp.status_code == 403
        regular_user.refresh_from_db()
        assert regular_user.role == "user"

    def test_cannot_change_super_admin_role(self, admin_client, super_admin, db):
        """A super admin's role cannot be changed by another super admin."""
        other_admin = User.objects.create_user(
            email="other-admin@example.com",
            password="pass123",
            role="super_admin",
            is_staff=True,
            is_superuser=True,
            is_email_verified=True,
        )
        resp = admin_client.put(
            f"/api/admin/users/{other_admin.id}/role",
            {"role": "user"},
            format="json",
        )
        assert resp.status_code == 403
        other_admin.refresh_from_db()
        assert other_admin.role == "super_admin"

    def test_invalid_role_returns_400(self, admin_client, regular_user):
        resp = admin_client.put(
            f"/api/admin/users/{regular_user.id}/role",
            {"role": "invalid_role"},
            format="json",
        )
        assert resp.status_code == 400

    def test_missing_role_field_returns_400(self, admin_client, regular_user):
        resp = admin_client.put(
            f"/api/admin/users/{regular_user.id}/role",
            {},
            format="json",
        )
        assert resp.status_code == 400

    def test_role_change_on_nonexistent_user_returns_404(self, admin_client):
        import uuid
        resp = admin_client.put(
            f"/api/admin/users/{uuid.uuid4()}/role",
            {"role": "supervisor"},
            format="json",
        )
        assert resp.status_code == 404


# ============================================================================
# AdminAuditLogsView tests
# ============================================================================

@pytest.mark.django_db
class TestAdminAuditLogs:
    def test_super_admin_can_view_user_logs(self, admin_client, regular_user):
        # First, perform an action that logs an audit event
        from core.utils import log_user_activity
        log_user_activity(regular_user, "test_action", {"key": "value"})

        resp = admin_client.get(f"/api/admin/users/{regular_user.id}/logs")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)
        assert len(resp.data) >= 1

    def test_supervisor_cannot_view_audit_logs(self, supervisor_client, regular_user):
        """Only super_admin can view audit logs — supervisor gets 403."""
        resp = supervisor_client.get(f"/api/admin/users/{regular_user.id}/logs")
        assert resp.status_code == 403


# ============================================================================
# AdminUserDetailView tests
# ============================================================================

@pytest.mark.django_db
class TestAdminUserDetail:
    def test_admin_can_view_user_details(self, admin_client, regular_user):
        resp = admin_client.get(f"/api/admin/users/{regular_user.id}/details")
        assert resp.status_code == 200
        assert resp.data["user"]["email"] == regular_user.email
        assert "total_amount_paid" in resp.data
        assert "total_images_generated" in resp.data
        assert "total_posts_generated" in resp.data
        assert "payments" in resp.data
        assert "onboarding" in resp.data

    def test_supervisor_can_view_user_details(self, supervisor_client, regular_user):
        resp = supervisor_client.get(f"/api/admin/users/{regular_user.id}/details")
        assert resp.status_code == 200

    def test_regular_user_cannot_view_user_details(self, user_client, regular_user):
        resp = user_client.get(f"/api/admin/users/{regular_user.id}/details")
        assert resp.status_code == 403

    def test_details_for_nonexistent_user_returns_404(self, admin_client):
        import uuid
        resp = admin_client.get(f"/api/admin/users/{uuid.uuid4()}/details")
        assert resp.status_code == 404