from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import UserActivityLog

class AdminUserActivityLogsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        if request.user.role != 'super_admin':
            return Response({"error": "Only super admins can access activity logs."}, status=status.HTTP_403_FORBIDDEN)
        
        logs = UserActivityLog.objects.filter(user_id=user_id).order_by('-created_at')
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': str(log.id),
                'action': log.action,
                'details': log.details,
                'created_at': log.created_at.isoformat()
            })
        return Response(logs_data)
