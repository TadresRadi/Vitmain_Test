from django.db import models

class Plan(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default='')
    features = models.TextField(blank=True, default='')  # Comma-separated or JSON list of features

    def __str__(self):
        return self.name
