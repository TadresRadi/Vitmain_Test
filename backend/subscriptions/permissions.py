"""
DRF permission classes for subscription-based access control.
"""
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from subscriptions.models import Subscription
from subscriptions.plan_access import CHAT_PLAN_SLUG


class HasActiveChatSubscription(permissions.BasePermission):
    """
    Permission class that allows access only to users with an active
    chat (basic) plan subscription.

    Returns appropriate HTTP status codes:
    - 402 Payment Required: No subscription found
    - 403 Forbidden: Subscription inactive or wrong plan
    """

    message = "No active subscription found. Plan selection is required."
    code = "payment_required"

    def has_permission(self, request, view):
        user = request.user

        try:
            sub = Subscription.objects.select_related("plan").get(user=user)
        except Subscription.DoesNotExist:
            raise PermissionDenied(
                detail={
                    "error": "No active subscription found. Plan selection is required.",
                }
            )

        if not sub.active:
            raise PermissionDenied(
                detail={"error": "Subscription is inactive."}
            )

        if sub.plan.slug != CHAT_PLAN_SLUG:
            raise PermissionDenied(
                detail={
                    "error": (
                        "Your plan does not include AI campaign generation. "
                        "Please use the Support page."
                    )
                }
            )

        return True