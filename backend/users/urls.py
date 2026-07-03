from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    MyTokenObtainPairView,
    RegisterView,
    UserProfileView,
    SupervisorCreateView,
    AdminUserListView,
    AdminUserRoleView,
    AdminUserActivityLogsView,
    UserUsageView,
    AdminOverviewView,
    AdminAuthLoginView,
    AdminAuthProfileView,
    GoogleOAuthCallbackView,
    GoogleAuthConfigView
)

urlpatterns = [
    path('auth/login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register', RegisterView.as_view(), name='auth_register'),
    path('users/profile', UserProfileView.as_view(), name='user_profile'),
    path('users/usage', UserUsageView.as_view(), name='user_usage'),
    
    # Google OAuth Endpoints
    path('auth/google/callback', GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
    path('auth/google/config', GoogleAuthConfigView.as_view(), name='google_oauth_config'),
    
    # Admin Auth Endpoints
    path('admin/auth/login', AdminAuthLoginView.as_view(), name='admin_auth_login'),
    path('admin/auth/profile', AdminAuthProfileView.as_view(), name='admin_auth_profile'),
    
    # Admin / Supervisor Endpoints
    path('admin/overview', AdminOverviewView.as_view(), name='admin_overview'),
    path('admin/create-supervisor', SupervisorCreateView.as_view(), name='admin_create_supervisor'),
    path('admin/users', AdminUserListView.as_view(), name='admin_users_list'),
    path('admin/users/<uuid:user_id>', AdminUserListView.as_view(), name='admin_user_detail'),
    path('admin/users/<uuid:user_id>/role', AdminUserRoleView.as_view(), name='admin_user_role'),
    path('admin/users/<uuid:user_id>/logs', AdminUserActivityLogsView.as_view(), name='admin_user_logs'),
]
