from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'auth_provider', 'role', 'user_type', 'is_active', 'date_joined', 'last_login']
    list_filter = ['auth_provider', 'role', 'user_type', 'is_active', 'date_joined']
    search_fields = ['email', 'full_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'full_name', 'phone_number', 'dob', 'profile_picture')
        }),
        ('Authentication', {
            'fields': ('auth_provider', 'is_active', 'is_staff', 'last_login')
        }),
        ('User Details', {
            'fields': ('role', 'user_type', 'language', 'onboarding_completed')
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def profile_picture_thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />', obj.profile_picture)
        return "No image"
    profile_picture_thumbnail.short_description = 'Profile Picture'
