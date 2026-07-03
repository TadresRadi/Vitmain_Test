from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    SuccessStoryViewSet,
    SuccessStorySettingsViewSet,
    FeaturedProjectViewSet,
    BrandViewSet,
    TeslaClientImageViewSet,
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'success-stories', SuccessStoryViewSet, basename='successstory')
router.register(r'success-story-settings', SuccessStorySettingsViewSet, basename='successstorysettings')
router.register(r'featured-projects', FeaturedProjectViewSet, basename='featuredproject')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'tesla-client-images', TeslaClientImageViewSet, basename='teslaclientimage')

urlpatterns = [
    path('', include(router.urls)),
]
