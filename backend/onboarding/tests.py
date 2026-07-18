
import pytest

from core.models import AuditLog
from onboarding.models import OnboardingResponse
from tests.factories import UserFactory


ONBOARDING_URL = "/api/onboarding/"


def onboarding_payload(**overrides):
    payload = {
        "business_name": "Vitamin Studio",
        "governorate": "Cairo",
        "business_type": "agency",
        "business_subtype": "marketing",
        "business_type_other": "",
        "marketing_goals": ["awareness", "leads"],
        "target_audience": "founders",
        "target_audience_other": "",
        "tone_of_voice": "confident",
        "tone_of_voice_other": "",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_onboarding_requires_authentication(client):
    response = client.get(ONBOARDING_URL)

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_returns_active_onboarding(auth_client):
    user = auth_client.handler._force_user
    OnboardingResponse.objects.create(
        user=user,
        is_active=False,
        **onboarding_payload(business_name="Old Studio"),
    )
    active = OnboardingResponse.objects.create(
        user=user,
        is_active=True,
        **onboarding_payload(business_name="Active Studio"),
    )

    response = auth_client.get(ONBOARDING_URL)

    assert response.status_code == 200
    assert response.data["business_name"] == active.business_name


@pytest.mark.django_db
def test_post_creates_onboarding_marks_user_complete_and_logs_activity(auth_client):
    user = auth_client.handler._force_user

    response = auth_client.post(ONBOARDING_URL, onboarding_payload(), format="json")

    assert response.status_code == 201
    user.refresh_from_db()
    onboarding = OnboardingResponse.objects.get(user=user)
    assert user.onboarding_completed is True
    assert onboarding.business_name == "Vitamin Studio"
    assert onboarding.is_active is True
    assert response.data["onboarding"]["business_name"] == "Vitamin Studio"
    assert AuditLog.objects.filter(
        user=user,
        action="onboarding_complete",
        details__onboarding_id=onboarding.pk,
    ).exists()


@pytest.mark.django_db
def test_post_updates_existing_active_onboarding_by_default(auth_client):
    user = auth_client.handler._force_user
    existing = OnboardingResponse.objects.create(
        user=user,
        is_active=True,
        **onboarding_payload(business_name="Before"),
    )

    response = auth_client.post(
        ONBOARDING_URL,
        onboarding_payload(business_name="After"),
        format="json",
    )

    assert response.status_code == 200
    assert OnboardingResponse.objects.filter(user=user).count() == 1
    existing.refresh_from_db()
    assert existing.business_name == "After"
    assert existing.is_active is True


@pytest.mark.django_db
def test_post_create_new_deactivates_previous_active_response(auth_client):
    user = auth_client.handler._force_user
    old = OnboardingResponse.objects.create(
        user=user,
        is_active=True,
        **onboarding_payload(business_name="Old"),
    )

    response = auth_client.post(
        ONBOARDING_URL,
        onboarding_payload(business_name="New", create_new=True),
        format="json",
    )

    assert response.status_code == 201
    old.refresh_from_db()
    assert old.is_active is False
    assert OnboardingResponse.objects.filter(user=user, is_active=True).get().business_name == "New"


@pytest.mark.django_db
def test_post_rejects_non_boolean_create_new(auth_client):
    response = auth_client.post(
        ONBOARDING_URL,
        onboarding_payload(create_new="yes"),
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"] == "create_new must be a boolean."


@pytest.mark.django_db
def test_get_falls_back_to_latest_inactive_onboarding(api_client):
    user = UserFactory()
    first = OnboardingResponse.objects.create(
        user=user,
        is_active=False,
        **onboarding_payload(business_name="First"),
    )
    latest = OnboardingResponse.objects.create(
        user=user,
        is_active=False,
        **onboarding_payload(business_name="Latest"),
    )
    from datetime import timedelta
    latest.created_at = first.created_at + timedelta(seconds=1)
    latest.save(update_fields=["created_at"])
    api_client.force_authenticate(user=user)

    response = api_client.get(ONBOARDING_URL)

    assert response.status_code == 200
    assert response.data["business_name"] == "Latest"

    

@pytest.mark.django_db
def test_get_returns_404_when_user_has_no_onboarding(auth_client):
    response = auth_client.get(ONBOARDING_URL)

    assert response.status_code == 404
    assert "error" in response.data


@pytest.mark.django_db
def test_post_requires_all_required_fields(auth_client):
    """Missing required fields should return 400."""
    response = auth_client.post(
        ONBOARDING_URL,
        {"business_name": "Only Name"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_post_creates_new_and_deactivates_previous(auth_client):
    """create_new=True should create a new active record and deactivate
    the previous active one."""
    user = auth_client.handler._force_user
    old = OnboardingResponse.objects.create(
        user=user,
        is_active=True,
        **onboarding_payload(business_name="Old Active"),
    )

    response = auth_client.post(
        ONBOARDING_URL,
        onboarding_payload(business_name="New Active", create_new=True),
        format="json",
    )

    assert response.status_code == 201
    old.refresh_from_db()
    assert old.is_active is False
    assert OnboardingResponse.objects.filter(user=user, is_active=True).count() == 1
    new_active = OnboardingResponse.objects.get(user=user, is_active=True)
    assert new_active.business_name == "New Active"


@pytest.mark.django_db
def test_post_updates_existing_active_by_default(auth_client):
    """Without create_new, POST updates the existing active record in place."""
    user = auth_client.handler._force_user
    existing = OnboardingResponse.objects.create(
        user=user,
        is_active=True,
        **onboarding_payload(business_name="Before"),
    )

    response = auth_client.post(
        ONBOARDING_URL,
        onboarding_payload(business_name="After"),
        format="json",
    )

    assert response.status_code == 200
    assert OnboardingResponse.objects.filter(user=user).count() == 1
    existing.refresh_from_db()
    assert existing.business_name == "After"
    assert existing.is_active is True


@pytest.mark.django_db
def test_post_rejects_non_boolean_create_new(auth_client):
    """create_new must be a boolean, not a string."""
    response = auth_client.post(
        ONBOARDING_URL,
        onboarding_payload(create_new="yes"),
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"] == "create_new must be a boolean."


@pytest.mark.django_db
def test_post_logs_audit_event(auth_client):
    """Each successful onboarding submission logs an audit event."""
    user = auth_client.handler._force_user

    auth_client.post(ONBOARDING_URL, onboarding_payload(), format="json")

    assert AuditLog.objects.filter(
        user=user,
        action="onboarding_complete",
    ).exists()


@pytest.mark.django_db
def test_post_marks_user_onboarding_completed(auth_client):
    """User.onboarding_completed is set to True after first submission."""
    user = auth_client.handler._force_user
    assert user.onboarding_completed is False

    auth_client.post(ONBOARDING_URL, onboarding_payload(), format="json")

    user.refresh_from_db()
    assert user.onboarding_completed is True


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access(auth_client):
    """An unauthenticated request gets 401."""
    from rest_framework.test import APIClient
    client = APIClient()
    response = client.get(ONBOARDING_URL)
    assert response.status_code == 401

    response = client.post(ONBOARDING_URL, onboarding_payload(), format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_returns_active_onboarding_even_when_inactive_exists(auth_client):
    """If user has both active and inactive records, GET returns the active one."""
    user = auth_client.handler._force_user
    OnboardingResponse.objects.create(
        user=user,
        is_active=False,
        **onboarding_payload(business_name="Inactive Old"),
    )
    active = OnboardingResponse.objects.create(
        user=user,
        is_active=True,
        **onboarding_payload(business_name="Active Current"),
    )

    response = auth_client.get(ONBOARDING_URL)

    assert response.status_code == 200
    assert response.data["business_name"] == "Active Current"
