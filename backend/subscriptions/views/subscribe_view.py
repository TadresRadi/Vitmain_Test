from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import log_user_activity
from subscriptions.models import Plan, Subscription
from subscriptions.serializers import SubscriptionSerializer
from subscriptions.plan_access import CHAT_PLAN_SLUG, SUPPORT_PLAN_SLUG


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_slug = request.data.get("plan_slug")
        if not plan_slug:
            return Response({"error": "plan_slug is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = Plan.objects.get(slug=plan_slug)
        except Plan.DoesNotExist:
            return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)

        # 200 EGP plan (basic) - redirect to Vodafone Cash payment page
        if plan.slug == "basic":
            # Return action to redirect to payment page
            return Response(
                {
                    "message": "Please complete payment verification.",
                    "action": "redirect_payment",
                    "plan_slug": plan.slug,
                    "plan_name": plan.name,
                    "amount": float(plan.price)
                }
            )

        if plan.slug == CHAT_PLAN_SLUG:
            subscription, _created = Subscription.objects.update_or_create(
                user=request.user,
                defaults={"plan": plan, "active": True},
            )
            log_user_activity(
                request.user,
                "subscription_activated",
                {"plan_name": plan.name, "price": float(plan.price)},
            )
            return Response(
                {
                    "message": "Subscription activated successfully.",
                    "subscription": SubscriptionSerializer(subscription).data,
                    "action": "redirect_chat",
                }
            )

        if plan.slug == SUPPORT_PLAN_SLUG:
            subscription, _created = Subscription.objects.update_or_create(
                user=request.user,
                defaults={"plan": plan, "active": True},
            )
            log_user_activity(
                request.user,
                "subscription_activated",
                {"plan_name": plan.name, "price": float(plan.price)},
            )
            return Response(
                {
                    "message": "Premium plan activated. Redirecting to support.",
                    "subscription": SubscriptionSerializer(subscription).data,
                    "action": "redirect_support",
                }
            )

        return Response({"error": "Unknown plan."}, status=status.HTTP_400_BAD_REQUEST)
