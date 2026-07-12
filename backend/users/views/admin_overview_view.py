from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription
from chat.models.generation_history import GeneratedPost, GeneratedImage
from django.db.models.functions import TruncDate
from django.db.models import Count, Sum

User = get_user_model()

class AdminOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['super_admin', 'supervisor']:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
            
        total_users = User.objects.filter(role='user').count()
        subscribed_users = Subscription.objects.filter(active=True, plan__slug='pro').count()
        
        # Count actual posts and images from the database
        total_posts = GeneratedPost.objects.count()
        total_images = GeneratedImage.objects.count()

        # Calculate total payments received from completed payment orders
        from payments.models import PaymentOrder
        total_payments = PaymentOrder.objects.filter(
            status=PaymentOrder.Status.COMPLETED
        ).aggregate(total=Sum('received_amount'))['total'] or 0

        # User growth mapping
        growth_qs = User.objects.filter(role='user').annotate(date=TruncDate('date_joined')).values('date').annotate(count=Count('id')).order_by('date')
        user_growth = [{"date": str(x['date']), "count": x['count']} for x in growth_qs]
        
        # Fallback for charts if empty
        if not user_growth:
            user_growth = [
                {"date": "2026-05-18", "count": 1},
                {"date": "2026-05-19", "count": total_users or 2},
                {"date": "2026-05-20", "count": total_users or 3}
            ]

        # Subscription distribution mapping
        dist_qs = Subscription.objects.filter(active=True).values('plan__slug', 'plan__name').annotate(count=Count('id'))
        subscription_distribution = [{"plan": x['plan__name'], "count": x['count']} for x in dist_qs]
        
        if not subscription_distribution:
            subscription_distribution = [
                {"plan": "Basic Plan", "count": max(0, total_users - subscribed_users)},
                {"plan": "Premium Plan", "count": subscribed_users}
            ]

        return Response({
            "total_users": total_users,
            "subscribed_users": subscribed_users,
            "total_payments": total_payments,
            "total_posts": total_posts,
            "total_images": total_images,
            "user_growth": user_growth,
            "subscription_distribution": subscription_distribution
        })
