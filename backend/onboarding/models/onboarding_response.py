from django.db import models
from django.conf import settings

class OnboardingResponse(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='onboarding_responses'
    )
    business_name = models.CharField(max_length=255)
    governorate = models.CharField(max_length=255, null=True, blank=True)
    business_type = models.CharField(max_length=255)
    business_subtype = models.CharField(max_length=255, null=True, blank=True)
    business_type_other = models.CharField(max_length=255, null=True, blank=True)
    marketing_goals = models.JSONField(default=list)  # Array of goals
    target_audience = models.CharField(max_length=255)
    target_audience_other = models.CharField(max_length=255, null=True, blank=True)
    tone_of_voice = models.CharField(max_length=255)
    tone_of_voice_other = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Flag to indicate which onboarding is currently active

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.business_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
