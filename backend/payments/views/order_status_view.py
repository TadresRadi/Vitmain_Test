from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.payment_order import PaymentOrder
from ..serializers.payment_order_serializer import PaymentOrderSerializer


class OrderStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        queryset = PaymentOrder.objects.select_related("user")

        if not request.user.is_staff:
            queryset = queryset.filter(user=request.user)

        try:
            order = queryset.get(pk=pk)
        except PaymentOrder.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = PaymentOrderSerializer(order).data
        data["subscription_active"] = (
            order.status == PaymentOrder.Status.COMPLETED
        )

        if order.status == PaymentOrder.Status.COMPLETED:
            data["next_url"] = (
                "/chat"
                if request.user.onboarding_completed
                else "/new-onboarding"
            )
        else:
            data["next_url"] = None

        return Response(data)