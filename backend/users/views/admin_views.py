import logging
from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import AuditLog
from core.utils import log_user_activity
from subscriptions.models import Subscription
from chat.models.generation_history import GeneratedPost, GeneratedImage
from users.serializers import CustomUserSerializer
from payments.models import PaymentOrder

logger = logging.getLogger(__name__)
User = get_user_model()

ADMIN_ROLES = {"super_admin", "supervisor"}
VALID_ROLES = ['user', 'supervisor', 'super_admin']


class AdminAuthLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {'error': 'Invalid admin credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'This account is inactive.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Allow both super_admin and supervisor roles to access admin portal
        if user.role not in ADMIN_ROLES:
            return Response(
                {'error': 'Access denied. Admin or supervisor privileges required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'role': user.role,
                'full_name': user.full_name,
            }
        }, status=status.HTTP_200_OK)


class AdminAuthProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in ADMIN_ROLES:
            return Response(
                {'error': 'Access denied. Admin or supervisor privileges required.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response({
            'id': str(request.user.id),
            'email': request.user.email,
            'role': request.user.role,
            'full_name': request.user.full_name,
        }, status=status.HTTP_200_OK)

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

class AdminAuditLogsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        if request.user.role != 'super_admin':
            return Response({"error": "Only super admins can access activity logs."}, status=status.HTTP_403_FORBIDDEN)
        
        logs = AuditLog.objects.filter(user_id=user_id).order_by('-created_at')
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': str(log.id),
                'action': log.action,
                'details': log.details,
                'created_at': log.created_at.isoformat()
            })
        return Response(logs_data)




class AdminUserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['super_admin', 'supervisor']:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        users = User.objects.all().order_by('-date_joined')
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def delete(self, request, user_id):
        if request.user.role != 'super_admin':
            return Response(
                {"error": "Only super admins can delete users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            UUID(str(user_id))
        except (TypeError, ValueError):
            return Response({"error": "Invalid user id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if str(user.id) == str(request.user.id):
            return Response(
                {"error": "You cannot delete your own account."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.role == 'super_admin':
            return Response(
                {"error": "Cannot delete a super admin account."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            with transaction.atomic():
                deleted_email = user.email
                user.delete()
            log_user_activity(
                request.user,
                'delete_user',
                {'deleted_user_id': str(user_id), 'deleted_email': deleted_email},
            )
            return Response(
                {"message": "User deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except IntegrityError as exc:
            logger.exception("IntegrityError while deleting user %s", user_id)
            return Response(
                {
                    "error": "Failed to delete user due to database integrity constraints.",
                    "details": str(exc) if settings.DEBUG else None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception:
            logger.exception("Unexpected error while deleting user %s", user_id)
            return Response(
                {
                    "error": "Failed to delete user. Please try again.",
                    "details": "Server error" if not settings.DEBUG else "See server logs.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminUserRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, user_id):
        if request.user.role != 'super_admin':
            return Response({"error": "Only super admins can update user roles."}, status=status.HTTP_403_FORBIDDEN)
        
        new_role = request.data.get('role')
        if not new_role:
            return Response({"error": "Role field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_role not in VALID_ROLES:
            return Response({"error": f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent changing super admin role
        if user.role == 'super_admin' and new_role != 'super_admin':
            return Response({"error": "Cannot change super admin role."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            old_role = user.role
            user.role = new_role
            
            # Set is_staff based on role
            user.is_staff = new_role in ['supervisor', 'super_admin']
            user.save()
            
            log_user_activity(
                request.user, 
                'update_user_role', 
                {'user_id': str(user.id), 'old_role': old_role, 'new_role': new_role}
            )
            
            return Response(
                {"message": "User role updated successfully.", "user": CustomUserSerializer(user).data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            error_message = str(e) if str(e) else "Failed to update user role"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
