from rest_framework import status
from rest_framework.response import Response

from subscriptions.models import Subscription

CHAT_PLAN_SLUG = "basic"
SUPPORT_PLAN_SLUG = "pro"


def get_user_plan_slug(user):
    try:
        sub = Subscription.objects.select_related("plan").get(user=user)
        if sub.active and sub.plan:
            return sub.plan.slug
    except Subscription.DoesNotExist:
        pass
    return None


def require_active_chat_subscription(user):
    """200 EGP (basic) plan — AI campaign / chat generation."""
    try:
        sub = Subscription.objects.select_related("plan").get(user=user)
    except Subscription.DoesNotExist:
        return Response(
            {"error": "No active subscription found. Plan selection is required."},
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )

    if not sub.active:
        return Response({"error": "Subscription is inactive."}, status=status.HTTP_403_FORBIDDEN)

    if sub.plan.slug != CHAT_PLAN_SLUG:
        return Response(
            {
                "error": "Your plan does not include AI campaign generation. Please use the Support page.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    return None
