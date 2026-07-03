import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class GenerationSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generation_sessions",
    )
    # Link to the post-generation record that created these images/posts
    post_generation = models.ForeignKey(
        "chat.AIPostGeneration",
        on_delete=models.CASCADE,
        related_name="generation_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["post_generation", "-created_at"]),
        ]


class GeneratedPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        GenerationSession,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    post_index = models.IntegerField()
    post_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("session", "post_index")
        ordering = ["post_index"]
        indexes = [
            models.Index(fields=["session", "post_index"]),
            models.Index(fields=["created_at"]),
        ]


class GeneratedImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        GeneratedPost,
        on_delete=models.CASCADE,
        related_name="images",
    )
    # absolute/relative URL can be returned; we also keep path for debugging
    image_url = models.TextField()
    image_path = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
        ]
