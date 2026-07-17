
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
    latest.created_at = first.created_at + (latest.created_at - first.created_at)
    latest.save(update_fields=["created_at"])
    api_client.force_authenticate(user=user)

    response = api_client.get(ONBOARDING_URL)

    assert response.status_code == 200
    assert response.data["business_name"] == "Latest"
