import logging

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import log_user_activity
from onboarding.models import OnboardingResponse
from onboarding.serializers import OnboardingResponseSerializer

logger = logging.getLogger(__name__)


class OnboardingResponseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        onboarding = OnboardingResponse.objects.filter(user=request.user, is_active=True).first()
        if not onboarding:
            onboarding = OnboardingResponse.objects.filter(user=request.user).order_by("-created_at").first()

        if not onboarding:
            return Response({"error": "Onboarding response not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OnboardingResponseSerializer(onboarding)
        return Response(serializer.data)

    def post(self, request):
        """
        Save onboarding answers only.

        Post generation must happen after plan selection (subscription), never during onboarding completion.
        """
        serializer = OnboardingResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_new = request.data.get("create_new", False)

        if create_new:
            OnboardingResponse.objects.filter(user=request.user).update(is_active=False)
            onboarding = OnboardingResponse.objects.create(
                user=request.user,
                **serializer.validated_data,
                is_active=True,
            )
            created = True
        else:
            onboarding, created = OnboardingResponse.objects.update_or_create(
                user=request.user,
                is_active=True,
                defaults=serializer.validated_data,
            )

        request.user.onboarding_completed = True
        request.user.save(update_fields=["onboarding_completed"])

        log_user_activity(
            request.user,
            "onboarding_complete",
            {
                **serializer.validated_data,
            },
        )

        return Response(
            {
                "message": "Onboarding answers saved successfully.",
                "onboarding": OnboardingResponseSerializer(onboarding).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
