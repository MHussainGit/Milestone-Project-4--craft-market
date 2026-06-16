from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models

from store.models import Product

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="United Kingdom")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} — {self.full_name} ({self.status})"

    def get_total(self) -> Decimal:
        return sum(item.get_line_total() for item in self.items.all())

    def get_total_pence(self) -> int:
        return int(self.get_total() * 100)

    def item_count(self) -> int:
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(
        validators=[__import__("django.core.validators", fromlist=["MinValueValidator"])
                    .MinValueValidator(1)]
    )
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["product__title"]

    def __str__(self):
        return f"{self.quantity}× {self.product.title}"

    def get_line_total(self) -> Decimal:
        return self.unit_price * self.quantity
