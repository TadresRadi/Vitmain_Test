
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from portfolio.models import (
    Brand,
    FeaturedProject,
    Project,
    SuccessStory,
    SuccessStorySettings,
    TeslaClientImage,
)
from tests.factories import UserFactory


def image_file(name="image.png"):
    return SimpleUploadedFile(
        name,
        b"tiny-image-content",
        content_type="image/png",
    )


@pytest.mark.django_db
def test_public_project_list_returns_only_active_projects(client):
    Project.objects.create(
        title="Active",
        description="Shown",
        category="Marketing",
        is_active=True,
        order=1,
    )
    Project.objects.create(
        title="Inactive",
        description="Hidden",
        category="Marketing",
        is_active=False,
        order=2,
    )

    response = client.get("/api/portfolio/projects/")

    assert response.status_code == 200
    assert [project["title"] for project in response.data] == ["Active"]


@pytest.mark.django_db
def test_non_admin_cannot_create_project(auth_client):
    response = auth_client.post(
        "/api/portfolio/projects/",
        {
            "title": "Blocked",
            "description": "Nope",
            "category": "Marketing",
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_supervisor_can_create_project(api_client):
    supervisor = UserFactory(role="supervisor", is_staff=True)
    api_client.force_authenticate(user=supervisor)

    response = api_client.post(
        "/api/portfolio/projects/",
        {
            "title": "Created",
            "description": "Allowed",
            "category": "Marketing",
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert Project.objects.filter(title="Created").exists()


@pytest.mark.django_db
def test_admin_all_action_includes_inactive_projects(api_client):
    admin = UserFactory(role="super_admin", is_staff=True, is_superuser=True)
    api_client.force_authenticate(user=admin)
    Project.objects.create(
        title="Active",
        description="Shown",
        category="Marketing",
        is_active=True,
    )
    Project.objects.create(
        title="Inactive",
        description="Admin only",
        category="Marketing",
        is_active=False,
    )

    response = api_client.get("/api/portfolio/projects/all/")

    assert response.status_code == 200
    assert {project["title"] for project in response.data} == {"Active", "Inactive"}


@pytest.mark.django_db
def test_featured_project_limit_is_enforced(api_client):
    admin = UserFactory(role="super_admin", is_staff=True, is_superuser=True)
    api_client.force_authenticate(user=admin)
    for index in range(6):
        FeaturedProject.objects.create(
            title=f"Featured {index}",
            description="Existing",
            category="Marketing",
        )

    response = api_client.post(
        "/api/portfolio/featured-projects/",
        {
            "title": "Too many",
            "description": "Blocked",
            "category": "Marketing",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "Maximum of 6 featured projects allowed." in str(response.data)


@pytest.mark.django_db
def test_success_story_settings_create_updates_existing_row(api_client):
    admin = UserFactory(role="super_admin", is_staff=True, is_superuser=True)
    api_client.force_authenticate(user=admin)
    story = SuccessStory.objects.create(
        content_en="English",
        content_ar="Arabic",
        is_active=True,
    )

    created = api_client.post(
        "/api/portfolio/success-story-settings/",
        {
            "mode": "manual",
            "rotation_interval": 30,
            "featured_video_id": story.id,
        },
        format="json",
    )
    updated = api_client.post(
        "/api/portfolio/success-story-settings/",
        {
            "mode": "auto",
            "rotation_interval": 45,
            "featured_video_id": story.id,
        },
        format="json",
    )

    assert created.status_code == 201
    assert updated.status_code == 200
    assert SuccessStorySettings.objects.count() == 1
    settings = SuccessStorySettings.objects.get()
    assert settings.mode == "auto"
    assert settings.rotation_interval == 45


@pytest.mark.django_db
def test_public_brand_and_tesla_lists_filter_inactive_items(client):
    Brand.objects.create(name="Active Brand", logo=image_file("brand.png"), is_active=True)
    Brand.objects.create(name="Inactive Brand", logo=image_file("brand2.png"), is_active=False)
    TeslaClientImage.objects.create(
        title="Active Tesla",
        image=image_file("tesla.png"),
        is_active=True,
    )
    TeslaClientImage.objects.create(
        title="Inactive Tesla",
        image=image_file("tesla2.png"),
        is_active=False,
    )

    brands = client.get("/api/portfolio/brands/")
    tesla = client.get("/api/portfolio/tesla-client-images/")

    assert brands.status_code == 200
    assert [brand["name"] for brand in brands.data] == ["Active Brand"]
    assert tesla.status_code == 200
    assert [image["title"] for image in tesla.data] == ["Active Tesla"]
