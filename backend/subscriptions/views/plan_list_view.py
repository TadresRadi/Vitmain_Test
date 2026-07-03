from rest_framework import permissions, generics
from subscriptions.models import Plan
from subscriptions.serializers import PlanSerializer

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
