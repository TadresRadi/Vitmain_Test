from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from subscriptions.models import Subscription
from subscriptions.serializers import SubscriptionSerializer

class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            subscription = Subscription.objects.get(user=request.user)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response({"active": False}, status=status.HTTP_200_OK)
