from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


ADMIN_ROLES = {"super_admin", "supervisor"}


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
