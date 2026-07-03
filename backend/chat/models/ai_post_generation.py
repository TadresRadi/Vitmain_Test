import uuid
from django.db import models
from django.conf import settings

class AIPostGeneration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_generations'
    )
    posts = models.JSONField(default=list)  # list of 5 posts
    edit_count = models.IntegerField(default=0)  # Must be limited to 1 total
    has_images = models.BooleanField(default=False)
    posts_review_complete = models.BooleanField(default=False)
    
    # Image generation status tracking
    images_status = models.CharField(
        max_length=20,
        default='not_started',
        choices=[
            ('not_started', 'Not Started'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ]
    )
    images_generation_started_at = models.DateTimeField(null=True, blank=True)
    images_generation_completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'posts_review_complete', '-created_at']),
            models.Index(fields=['user', 'images_status']),
        ]
        # Ensure only one active post generation per user at a time
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(posts_review_complete=False),
                name='unique_active_post_generation_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - Posts Gen {self.id} (Edits: {self.edit_count}, Images: {self.images_status})"
