import pytest

from chat.models import AIChatMessage, AIChatSession, AIPostGeneration
from subscriptions.models import Subscription
from tests.factories import AIPostGenerationFactory, OnboardingResponseFactory


PREMIUM_POSTS_URL = "/api/chat/premium-posts"


@pytest.mark.django_db
def test_get_premium_posts_requires_onboarding(auth_client):
    response = auth_client.get(PREMIUM_POSTS_URL)

    assert response.status_code == 400
    assert "onboarding" in response.data["error"].lower()


@pytest.mark.django_db
def test_get_premium_posts_seeds_chat_session_and_returns_existing_generation(auth_client):
    user = auth_client.handler._force_user
    OnboardingResponseFactory(user=user, business_name="Vitamin")
    post_generation = AIPostGenerationFactory(user=user)

    response = auth_client.get(PREMIUM_POSTS_URL)

    assert response.status_code == 200
    assert response.data["post_generation"]["id"] == str(post_generation.id)
    assert AIChatSession.objects.filter(user=user).exists()
    assert AIChatMessage.objects.filter(session__user=user).count() == 12


@pytest.mark.django_db
def test_post_premium_posts_requires_active_chat_subscription(auth_client):
    user = auth_client.handler._force_user
    OnboardingResponseFactory(user=user)

    response = auth_client.post(PREMIUM_POSTS_URL, {}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_post_premium_posts_returns_existing_in_progress_generation(auth_client, basic_plan):
    user = auth_client.handler._force_user
    OnboardingResponseFactory(user=user)
    Subscription.objects.create(user=user, plan=basic_plan, active=True)
    existing = AIPostGenerationFactory(user=user, posts_review_complete=False)

    response = auth_client.post(PREMIUM_POSTS_URL, {}, format="json")

    assert response.status_code == 200
    assert response.data["post_generation"]["id"] == str(existing.id)
    assert response.data["message"] == "Posts already exist, returning existing data."


@pytest.mark.django_db
def test_post_premium_posts_force_regenerate_calls_ai_and_persists(auth_client, basic_plan, monkeypatch):
    user = auth_client.handler._force_user
    OnboardingResponseFactory(user=user)
    Subscription.objects.create(user=user, plan=basic_plan, active=True)
    existing = AIPostGenerationFactory(user=user, posts_review_complete=False)
    new_posts = ["New 1", "New 2", "New 3", "New 4", "New 5"]

    monkeypatch.setattr(
        "chat.views.premium_posts_view.generate_posts_from_onboarding",
        lambda onboarding, user_lang: (new_posts, True, None),
    )

    response = auth_client.post(
        PREMIUM_POSTS_URL,
        {"force_regenerate": True},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["posts"] == new_posts
    assert AIPostGeneration.objects.filter(user=user).count() == 2
    assert response.data["post_generation"]["id"] != str(existing.id)
    user.refresh_from_db()
    assert user.posts_generated is True


@pytest.mark.django_db
def test_post_premium_posts_returns_503_when_ai_unavailable(auth_client, basic_plan, monkeypatch):
    user = auth_client.handler._force_user
    OnboardingResponseFactory(user=user)
    Subscription.objects.create(user=user, plan=basic_plan, active=True)

    monkeypatch.setattr(
        "chat.views.premium_posts_view.generate_posts_from_onboarding",
        lambda onboarding, user_lang: ([], False, "missing key"),
    )

    response = auth_client.post(PREMIUM_POSTS_URL, {}, format="json")

    assert response.status_code == 503
    assert "currently unavailable" in response.data["error"]
