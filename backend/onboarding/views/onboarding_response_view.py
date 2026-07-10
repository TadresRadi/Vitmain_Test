import logging

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import log_user_activity
from onboarding.models import OnboardingResponse
from onboarding.serializers import OnboardingResponseSerializer
from django.db import transaction

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

    @transaction.atomic
    def post(self, request):
        serializer = OnboardingResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_new = request.data.get("create_new", False)
        if not isinstance(create_new, bool):
            return Response({"error": "create_new must be a boolean."},status=status.HTTP_400_BAD_REQUEST,)

        active_responses = (
            OnboardingResponse.objects
            .select_for_update()
            .filter(user=request.user, is_active=True)
            .order_by("-created_at"))
        active_onboarding = active_responses.first()

        if create_new or active_onboarding is None:
            active_responses.update(is_active=False)

            onboarding = OnboardingResponse.objects.create(
            user=request.user,
            is_active=True,
            **serializer.validated_data,)
            created = True
        else:
        # Repair old duplicate-active records before updating.
            active_responses.exclude(pk=active_onboarding.pk).update(is_active=False)

            for field, value in serializer.validated_data.items():
                setattr(active_onboarding, field, value)

            active_onboarding.is_active = True
            active_onboarding.save()
            onboarding = active_onboarding
            created = False

        if not request.user.onboarding_completed:
            request.user.onboarding_completed = True
            request.user.save(update_fields=["onboarding_completed"])

        log_user_activity(
            request.user,
            "onboarding_complete",
            {"onboarding_id": onboarding.pk},
        )

        return Response(
        {"message": "Onboarding answers saved successfully.","onboarding": OnboardingResponseSerializer(onboarding).data,},
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK),)
