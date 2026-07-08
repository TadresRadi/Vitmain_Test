from django.contrib import admin
from .models import Project, SuccessStory, SuccessStorySettings, TeslaClientImage


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'category']
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    ordering = ['-created_at']


@admin.register(SuccessStorySettings)
class SuccessStorySettingsAdmin(admin.ModelAdmin):
    list_display = ['mode', 'rotation_interval', 'updated_at']
    list_filter = ['mode', 'updated_at']
    ordering = ['-updated_at']


@admin.register(TeslaClientImage)
class TeslaClientImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']
