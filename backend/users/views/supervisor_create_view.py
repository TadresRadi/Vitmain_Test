from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from core.utils import log_user_activity
from users.serializers import CustomUserSerializer, SupervisorCreateSerializer
from users.permissions import IsSuperAdmin

class SupervisorCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    def post(self, request):
        
        serializer = SupervisorCreateSerializer(data=request.data)
        if not serializer.is_valid():
            # Convert validation errors to a consistent format
            errors = serializer.errors
            error_message = None
            if isinstance(errors, dict):
                # Get the first error message from the first field
                for field, messages in errors.items():
                    if isinstance(messages, list) and messages:
                        error_message = messages[0]
                    else:
                        error_message = str(messages)
                    break
            error_message = error_message or "Validation failed"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            supervisor = serializer.save()
            log_user_activity(request.user, 'create_supervisor', {'supervisor_email': supervisor.email})
            return Response(
                {"message": "Supervisor created successfully.", "user": CustomUserSerializer(supervisor).data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            error_message = str(e) if str(e) else "Failed to create supervisor"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
