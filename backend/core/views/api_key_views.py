"""
API Key management views.
"""
import logging
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from core.api_key_models import APIKey
from core.api_key_service import get_api_key_service
from core.exceptions import ValidationError, AuthorizationError

User = get_user_model()
logger = logging.getLogger(__name__)


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing API keys.
    
    List: GET /api/api-keys/
    Create: POST /api/api-keys/
    Retrieve: GET /api/api-keys/{id}/
    Update: PATCH /api/api-keys/{id}/
    Destroy: DELETE /api/api-keys/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = None  # Will be imported
    
    def get_queryset(self):
        """Only show user's own keys."""
        return APIKey.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """List all API keys for current user."""
        try:
            api_key_service = get_api_key_service()
            keys = api_key_service.get_user_keys(
                request.user,
                include_inactive=True
            )
            
            # Serialize (don't expose key_hash)
            data = [
                {
                    'id': str(k.id),
                    'name': k.name,
                    'key_prefix': k.key_prefix,
                    'scope': k.scope,
                    'status': k.status,
                    'created_at': k.created_at.isoformat(),
                    'expires_at': k.expires_at.isoformat() if k.expires_at else None,
                    'last_used_at': k.last_used_at.isoformat() if k.last_used_at else None,
                    'description': k.description,
                }
                for k in keys
            ]
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.exception("Error listing API keys")
            raise ValidationError("Failed to list API keys")

    def create(self, request, *args, **kwargs):
        """Create new API key."""
        try:
            name = request.data.get('name', '').strip()
            scope = request.data.get('scope', 'read')
            expires_in_days = request.data.get('expires_in_days')
            description = request.data.get('description', '')
            allowed_ips = request.data.get('allowed_ips', [])
            
            # Validate
            if not name or len(name) < 3:
                raise ValidationError("Key name must be at least 3 characters")
            
            valid_scopes = ['read', 'write', 'admin']
            if scope not in valid_scopes:
                raise ValidationError(f"Invalid scope: {scope}")
            
            # Create key
            api_key_service = get_api_key_service()
            raw_key, api_key = api_key_service.create_api_key(
                user=request.user,
                name=name,
                scope=scope,
                expires_in_days=expires_in_days,
                description=description,
                allowed_ips=allowed_ips,
            )
            
            return Response(
                {
                    'id': str(api_key.id),
                    'name': api_key.name,
                    'key': raw_key,  # Only shown once on creation
                    'key_prefix': api_key.key_prefix,
                    'scope': api_key.scope,
                    'status': api_key.status,
                    'created_at': api_key.created_at.isoformat(),
                    'message': 'Save this key securely. You won\'t be able to see it again.',
                },
                status=status.HTTP_201_CREATED
            )
        
        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Error creating API key")
            raise ValidationError("Failed to create API key")

    def destroy(self, request, pk=None, *args, **kwargs):
        """Revoke API key."""
        try:
            api_key = self.get_object()
            
            if api_key.user != request.user:
                raise AuthorizationError("Cannot revoke another user's key")
            
            reason = request.data.get('reason', 'User revoked')
            
            api_key_service = get_api_key_service()
            api_key_service.revoke_key(api_key, request.user, reason)
            
            return Response(
                {'message': 'API key revoked'},
                status=status.HTTP_200_OK
            )
        
        except AuthorizationError:
            raise
        except Exception as e:
            logger.exception("Error revoking API key")
            raise ValidationError("Failed to revoke API key")

    @action(detail=True, methods=['post'])
    def rotate(self, request, pk=None, *args, **kwargs):
        """
        Rotate an API key.
        
        POST /api/api-keys/{id}/rotate/
        """
        try:
            api_key = self.get_object()
            
            if api_key.user != request.user:
                raise AuthorizationError("Cannot rotate another user's key")
            
            api_key_service = get_api_key_service()
            raw_key, new_api_key = api_key_service.rotate_key(
                api_key,
                request.user
            )
            
            return Response(
                {
                    'id': str(new_api_key.id),
                    'name': new_api_key.name,
                    'key': raw_key,
                    'key_prefix': new_api_key.key_prefix,
                    'scope': new_api_key.scope,
                    'created_at': new_api_key.created_at.isoformat(),
                    'message': 'Old key is now inactive. Save this new key securely.',
                },
                status=status.HTTP_201_CREATED
            )
        
        except AuthorizationError:
            raise
        except Exception as e:
            logger.exception("Error rotating API key")
            raise ValidationError("Failed to rotate API key")

    @action(detail=False, methods=['get'])
    def usage(self, request, *args, **kwargs):
        """
        Get API key usage statistics.
        
        GET /api/api-keys/usage/
        """
        try:
            keys = self.get_queryset()
            
            usage_data = []
            for key in keys:
                usage_data.append({
                    'name': key.name,
                    'last_used_at': key.last_used_at.isoformat() if key.last_used_at else None,
                    'last_ip': key.last_ip,
                    'total_audit_logs': key.audit_logs.count(),
                })
            
            return Response(usage_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.exception("Error getting API key usage")
            raise ValidationError("Failed to get usage statistics")