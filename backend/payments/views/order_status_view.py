from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models.payment_order import PaymentOrder
from ..serializers.payment_order_serializer import PaymentOrderSerializer

class OrderStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            order = PaymentOrder.objects.get(pk=pk)
            if order.user != request.user and not request.user.is_staff:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = PaymentOrderSerializer(order)
            response_data = serializer.data
            response_data['subscription_active'] = (order.status == PaymentOrder.Status.COMPLETED)
            return Response(response_data, status=status.HTTP_200_OK)
        except PaymentOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)