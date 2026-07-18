"""
DRF permission classes for role-based access control.

Usage:
    from users.permissions import IsAdminOrSupervisor, IsSuperAdmin

    class MyView(APIView):
        permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
"""
from rest_framework import permissions


class IsAdminOrSupervisor(permissions.BasePermission):
    """
    Allows access to super_admin and supervisor roles only.
    Use for admin endpoints that both roles can access (read, overview).
    """

    message = "Access denied. Admin or supervisor privileges required."
    code = "not_admin_or_supervisor"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('super_admin', 'supervisor')


class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access to super_admin role only.
    Use for destructive operations (delete, role change, supervisor creation).
    """

    message = "Access denied. Super admin privileges required."
    code = "not_super_admin"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'super_admin'