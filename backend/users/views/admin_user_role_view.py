from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from users.serializers import CustomUserSerializer
from core.utils import log_user_activity

User = get_user_model()

VALID_ROLES = ['user', 'supervisor', 'super_admin']

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
