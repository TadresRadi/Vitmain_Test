from .auth_views import (
    MyTokenObtainPairView,
    RegisterView,
    GoogleOAuthCallbackView,
    GoogleAuthConfigView,
     LogoutView,
)
from .supervisor_create_view import SupervisorCreateView
from .profile_views import UserProfileView
from .user_usage_view import UserUsageView

from .admin_views import (
    AdminUserListView,
    AdminUserRoleView,
    AdminAuditLogsView,
    AdminOverviewView,
    AdminAuthLoginView,
    AdminAuthProfileView,
    AdminUserDetailView,
)
from .password_views import (
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetView,
    PasswordStrengthCheckView,
)

__all__ = [
    "MyTokenObtainPairView",
    "RegisterView",
    "GoogleOAuthCallbackView",
    "GoogleAuthConfigView",
    "UserProfileView",
    "UserUsageView",
    "SupervisorCreateView",
    "AdminUserListView",
    "AdminUserRoleView",
    "AdminAuditLogsView",
    "AdminOverviewView",
    "AdminAuthLoginView",
    "AdminAuthProfileView",
    "AdminUserDetailView",
    'LogoutView',

    'PasswordChangeView',
    'PasswordResetRequestView',
    'PasswordResetView',
    'PasswordStrengthCheckView',
]