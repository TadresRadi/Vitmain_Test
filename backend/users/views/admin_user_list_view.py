from uuid import UUID

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.utils import IntegrityError
from django.conf import settings
import logging

from users.serializers import CustomUserSerializer
from core.utils import log_user_activity

logger = logging.getLogger(__name__)

User = get_user_model()


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
