from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class SuccessStory(models.Model):
    content_en = models.TextField()
    content_ar = models.TextField()
    video = models.FileField(upload_to='success-stories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Success Stories"

    def __str__(self):
        return f"Success Story {self.id}"


class SuccessStorySettings(models.Model):
    MODE_CHOICES = [
        ('auto', 'Auto'),
        ('manual', 'Manual'),
    ]

    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='auto')
    rotation_interval = models.IntegerField(default=24)  # in seconds
    featured_video = models.ForeignKey('SuccessStory', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_in_settings')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Success Story Settings"

    def __str__(self):
        return f"Settings: {self.mode} mode, {self.rotation_interval}s interval"


class FeaturedProject(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='featured-projects/', null=True, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = "Featured Projects"

    def __str__(self):
        return self.title


class Brand(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='brands/')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name


class TeslaClientImage(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    image = models.ImageField(upload_to='tesla-client/')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Tesla Client Image"
        verbose_name_plural = "Tesla Client Images"

    def __str__(self):
        return self.title or f"Tesla Client Image {self.id}"
