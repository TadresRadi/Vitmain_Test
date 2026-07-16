from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission
from .models import Project, SuccessStory, SuccessStorySettings, FeaturedProject, Brand, TeslaClientImage
from .serializers import (
    ProjectSerializer,
    SuccessStorySerializer,
    SuccessStorySettingsSerializer,
    FeaturedProjectSerializer,
    BrandSerializer,
    TeslaClientImageSerializer,
)


class IsAdminOrSupervisor(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in {"super_admin", "supervisor"}
        )


class NoPagination(PageNumberPagination):
    """Disable pagination — portfolio endpoints return small lists as bare arrays."""
    page_size = None
    page_size_query_param = None
    paginate_by_param = None


class PublicReadAdminWriteMixin:
    public_actions = {"list", "retrieve"}
    pagination_class = None  # All portfolio viewsets return bare arrays, not paginated wrappers

    def get_permissions(self):
        permission_classes = [AllowAny] if self.action in self.public_actions else [IsAdminOrSupervisor]
        return [permission() for permission in permission_classes]
class ProjectViewSet(PublicReadAdminWriteMixin, viewsets.ModelViewSet):
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectSerializer
    ordering = ['order', '-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all projects including inactive ones (for admin)"""
        projects = Project.objects.all()
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)


class SuccessStoryViewSet(PublicReadAdminWriteMixin, viewsets.ModelViewSet):
    queryset = SuccessStory.objects.all()
    serializer_class = SuccessStorySerializer

    def get_queryset(self):
        # For list action, only return active stories
        if self.action == 'list':
            return SuccessStory.objects.filter(is_active=True)
        return SuccessStory.objects.all()

    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all success stories including inactive ones (for admin)"""
        stories = SuccessStory.objects.all()
        serializer = self.get_serializer(stories, many=True)
        return Response(serializer.data)


class SuccessStorySettingsViewSet(PublicReadAdminWriteMixin, viewsets.ModelViewSet):
    queryset = SuccessStorySettings.objects.all()
    serializer_class = SuccessStorySettingsSerializer
    pagination_class = None  # Only one settings row ever exists; return a bare array

    def get_queryset(self):
        # There should only be one settings object, but don't limit for detail views
        if self.action == 'list':
            return SuccessStorySettings.objects.all()[:1]
        return SuccessStorySettings.objects.all()

    def create(self, request, *args, **kwargs):
        # Ensure only one settings object exists
        if SuccessStorySettings.objects.exists():
            # Update existing settings instead of creating new
            existing = SuccessStorySettings.objects.first()
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)


class FeaturedProjectViewSet(PublicReadAdminWriteMixin, viewsets.ModelViewSet):
    queryset = FeaturedProject.objects.all()
    serializer_class = FeaturedProjectSerializer
    ordering = ['order', '-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all featured projects including inactive ones (for admin)"""
        projects = FeaturedProject.objects.all()
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)


class BrandViewSet(PublicReadAdminWriteMixin, viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    ordering = ['order', '-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all brands including inactive ones (for admin)"""
        brands = Brand.objects.all()
        serializer = self.get_serializer(brands, many=True)
        return Response(serializer.data)


class TeslaClientImageViewSet(PublicReadAdminWriteMixin, viewsets.ModelViewSet):
    queryset = TeslaClientImage.objects.all()
    serializer_class = TeslaClientImageSerializer
    ordering = ['order', '-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all Tesla Client images including inactive ones (for admin)"""
        images = TeslaClientImage.objects.all()
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)
