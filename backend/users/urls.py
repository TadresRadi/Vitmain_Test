from django.urls import path
from users.views.auth_views import (
    MyTokenObtainPairView,
    RegisterView,
    GoogleOAuthCallbackView,
    GoogleAuthConfigView,
    LogoutView,
    CookieTokenRefreshView,
    VerifyEmailView,
    ResendVerificationView,
)
from users.views import (
    UserProfileView,
    UserUsageView,
    AdminUserListView,
    AdminUserRoleView,
    AdminAuditLogsView,
    AdminOverviewView,
    AdminAuthLoginView,
    AdminAuthProfileView,
    AdminUserDetailView,
    SupervisorCreateView,
)
from users.views.password_views import (
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetView,
    PasswordStrengthCheckView,
)

urlpatterns = [
    # Authentication
    path('auth/login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register', RegisterView.as_view(), name='auth_register'),
    path('auth/verify-email', VerifyEmailView.as_view(), name='verify_email'),
    path('auth/resend-verification', ResendVerificationView.as_view(), name='resend_verification'),

    # Google OAuth
    path('auth/google/callback', GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
    path('auth/google/config', GoogleAuthConfigView.as_view(), name='google_oauth_config'),

    # User Profile
    path('users/profile', UserProfileView.as_view(), name='user_profile'),
    path('users/usage', UserUsageView.as_view(), name='user_usage'),

    # Admin Authentication
    path('admin/auth/login', AdminAuthLoginView.as_view(), name='admin_auth_login'),
    path('admin/auth/profile', AdminAuthProfileView.as_view(), name='admin_auth_profile'),

    # Admin Management
    path('admin/overview', AdminOverviewView.as_view(), name='admin_overview'),
    path('admin/create-supervisor', SupervisorCreateView.as_view(), name='admin_create_supervisor'),
    path('admin/users', AdminUserListView.as_view(), name='admin_users_list'),
    path('admin/users/<uuid:user_id>', AdminUserListView.as_view(), name='admin_user_detail'),
    path('admin/users/<uuid:user_id>/role', AdminUserRoleView.as_view(), name='admin_user_role'),
    path('admin/users/<uuid:user_id>/logs', AdminAuditLogsView.as_view(), name='admin_user_logs'),
    path('admin/users/<uuid:user_id>/details', AdminUserDetailView.as_view(), name='admin_user_details'),
    path('auth/logout', LogoutView.as_view(), name='logout'),

    # Password Management
    path('auth/password/change', PasswordChangeView.as_view(), name='password_change'),
    path('auth/password/reset-request', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password/reset', PasswordResetView.as_view(), name='password_reset'),
    path('auth/password/strength', PasswordStrengthCheckView.as_view(), name='password_strength'),
]