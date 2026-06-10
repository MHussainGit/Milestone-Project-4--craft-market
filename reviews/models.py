from django.contrib.auth import get_user_model
from django.db import models

from store.models import Product

User = get_user_model()


class Review(models.Model):
    RATING_CHOICES = [
        (1, "1 — Poor"),
        (2, "2 — Fair"),
        (3, "3 — Good"),
        (4, "4 — Very Good"),
        (5, "5 — Excellent"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    headline = models.CharField(max_length=200)
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["product", "user"]]

    def __str__(self):
        return f"{self.user.username} on '{self.product.title}' ({self.rating}★)"
