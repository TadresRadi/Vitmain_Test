
import pytest

from core.models import AuditLog
from support.models import SupportChat, SupportMessage
from tests.factories import UserFactory


SUPPORT_URL = "/api/support/chat"
ADMIN_CHATS_URL = "/api/admin/support/chats"
ADMIN_REPLY_URL = "/api/admin/support/reply"


@pytest.mark.django_db
def test_user_get_starts_support_chat_with_welcome_message(auth_client):
    user = auth_client.handler._force_user

    response = auth_client.get(SUPPORT_URL)

    assert response.status_code == 200
    chat = SupportChat.objects.get(user=user)
    assert response.data["id"] == str(chat.id)
    assert chat.messages.count() == 1
    assert chat.messages.first().content == "Welcome! How can we help you today?"
    assert AuditLog.objects.filter(user=user, action="start_support_chat").exists()


@pytest.mark.django_db
def test_user_can_send_support_message(auth_client):
    user = auth_client.handler._force_user

    response = auth_client.post(
        SUPPORT_URL,
        {"content": "I need help"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["content"] == "I need help"
    assert SupportMessage.objects.filter(sender=user, content="I need help").exists()
    assert AuditLog.objects.filter(user=user, action="send_support_message").exists()


@pytest.mark.django_db
def test_user_support_message_requires_content(auth_client):
    response = auth_client.post(SUPPORT_URL, {}, format="json")

    assert response.status_code == 400
    assert response.data["error"] == "content is required."


@pytest.mark.django_db
def test_non_admin_cannot_list_support_chats(auth_client):
    response = auth_client.get(ADMIN_CHATS_URL)

    assert response.status_code == 403


@pytest.mark.django_db
def test_supervisor_can_list_support_chats(api_client):
    user = UserFactory()
    supervisor = UserFactory(role="supervisor", is_staff=True)
    SupportChat.objects.create(user=user)
    api_client.force_authenticate(user=supervisor)

    response = api_client.get(ADMIN_CHATS_URL)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["user_email"] == user.email


@pytest.mark.django_db
def test_admin_can_reply_to_support_chat(api_client):
    user = UserFactory()
    admin = UserFactory(role="super_admin", is_staff=True, is_superuser=True)
    chat = SupportChat.objects.create(user=user)
    api_client.force_authenticate(user=admin)

    response = api_client.post(
        ADMIN_REPLY_URL,
        {"chat_id": str(chat.id), "content": "We are on it"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["content"] == "We are on it"
    assert SupportMessage.objects.filter(chat=chat, sender=admin).exists()
    assert AuditLog.objects.filter(user=admin, action="admin_reply_support").exists()


@pytest.mark.django_db
def test_admin_reply_validates_required_fields(api_client):
    admin = UserFactory(role="super_admin", is_staff=True, is_superuser=True)
    api_client.force_authenticate(user=admin)

    response = api_client.post(ADMIN_REPLY_URL, {"content": "Missing chat"}, format="json")

    assert response.status_code == 400
    assert response.data["error"] == "chat_id and content are required."
