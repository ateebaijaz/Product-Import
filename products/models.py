from django.db import models
from django.db.models.functions import Lower

class Product(models.Model):
    sku = models.CharField(max_length=100)
    sku_lower = models.CharField(max_length=100, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('sku_lower',),)
        indexes = [
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return self.sku


