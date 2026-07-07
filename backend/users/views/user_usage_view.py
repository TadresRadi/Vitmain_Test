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
            # Get subscription and plan with safe getattr usage
            sub = Subscription.objects.select_related("plan").get(user=request.user)
            plan = getattr(sub, "plan", None)

            plan_slug = getattr(plan, "slug", None) if plan is not None else None
            plan_name = getattr(plan, "name", None) if plan is not None else None
            has_access = bool(getattr(sub, "active", False)) and plan_slug == CHAT_PLAN_SLUG

            # Determine max_images safely (Plan model may not have this field)
            max_images = None
            if plan is not None:
                max_images = getattr(plan, "max_images", None)
                if max_images is None:
                    max_images = getattr(plan, "image_limit", None)
                if max_images is None:
                    max_images = getattr(plan, "max_images_per_month", None)
            if max_images is None:
                max_images = 0
        except Subscription.DoesNotExist:
            plan_slug = None
            plan_name = None
            has_access = False
            max_images = 0

        # Get total images generated for this user by following relations:
        # GeneratedImage -> post -> session -> user
        total_images = GeneratedImage.objects.filter(post__session__user=request.user).count()

        # Get total amount paid by this user from completed payment orders
        from payments.models import PaymentOrder
        total_amount_paid = PaymentOrder.objects.filter(
            user=request.user,
            status=PaymentOrder.Status.COMPLETED
        ).aggregate(total=Sum('received_amount'))['total'] or 0

        # Compute remaining images if applicable
        try:
            remaining_images = max(0, int(max_images) - total_images) if isinstance(max_images, (int, float, str)) else 0
        except Exception:
            remaining_images = 0

        return Response({
            "has_access": has_access,
            "plan_slug": plan_slug,
            "plan_name": plan_name,
            "total_images": total_images,
            "max_images": int(max_images) if isinstance(max_images, (int, float)) else 0,
            "remaining_images": remaining_images,
            "total_amount_paid": total_amount_paid,
        })