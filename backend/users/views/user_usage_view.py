from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum

from subscriptions.models import Subscription
from subscriptions.plan_access import CHAT_PLAN_SLUG
from chat.models.generation_history import GeneratedImage


class UserUsageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            sub = Subscription.objects.select_related("plan").get(user=request.user)
            plan_slug = sub.plan.slug if sub.plan else None
            plan_name = sub.plan.name if sub.plan else None
            has_access = sub.active and plan_slug == CHAT_PLAN_SLUG
            max_images = sub.plan.max_images if sub.plan else 0
        except Subscription.DoesNotExist:
            plan_slug = None
            plan_name = None
            has_access = False
            max_images = 0

        # Get total images generated for this user
        total_images = GeneratedImage.objects.filter(
            post__session__user=request.user
        ).count()

        # Get total amount paid by this user from completed payment orders
        from payments.models import PaymentOrder
        total_amount_paid = PaymentOrder.objects.filter(
            user=request.user,
            status=PaymentOrder.Status.COMPLETED
        ).aggregate(total=Sum('received_amount'))['total'] or 0

        return Response({
            "has_access": has_access,
            "plan_slug": plan_slug,
            "plan_name": plan_name,
            "total_images": total_images,
            "max_images": max_images,
            "remaining_images": 0,  # Always 0 as per requirements
            "total_amount_paid": total_amount_paid,
        })
