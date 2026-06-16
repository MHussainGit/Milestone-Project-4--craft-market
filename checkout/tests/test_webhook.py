"""
Stripe webhook tests.

Run with: pytest checkout/tests/test_webhook.py -v
"""

import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from checkout.models import Order, OrderItem
from store.models import Category, Product, Shop

User = get_user_model()


def _make_order(status="pending"):
    user = User.objects.create_user(f"webhookuser_{Order.objects.count()}", password="pass")
    return Order.objects.create(
        user=user,
        full_name="Webhook User",
        email="webhook@example.com",
        address_line1="1 Webhook St",
        city="Webhookville",
        postcode="WH1 1WH",
        status=status,
    )


def _make_product(stock=10):
    owner = User.objects.create_user(f"shopowner_{Product.objects.count()}", password="pass")
    shop = Shop.objects.create(user=owner, name=f"Shop {Product.objects.count()}")
    category = Category.objects.create(name=f"Category {Product.objects.count()}")
    return Product.objects.create(
        title=f"Product {Product.objects.count()}",
        shop=shop,
        category=category,
        price="10.00",
        stock=stock,
    )


class StripeWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _post_webhook(self, event_type, order_pk):
        payload = json.dumps({
            "type": event_type,
            "data": {
                "object": {
                    "id": "pi_test_123",
                    "metadata": {"order_pk": str(order_pk)},
                }
            }
        }).encode()

        fake_event = {
            "type": event_type,
            "data": {
                "object": {
                    "id": "pi_test_123",
                    "metadata": {"order_pk": str(order_pk)},
                }
            }
        }
        with patch("checkout.views.stripe.Webhook.construct_event", return_value=fake_event):
            response = self.client.post(
                reverse("stripe_webhook"),
                data=payload,
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="t=123,v1=abc",
            )
        return response

    def test_webhook_payment_intent_succeeded_marks_order_paid(self):
        order = _make_order(status="pending")
        self.assertEqual(order.status, "pending")
        response = self._post_webhook("payment_intent.succeeded", order.pk)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, "paid")

    def test_webhook_already_paid_order_not_double_processed(self):
        order = _make_order(status="paid")
        response = self._post_webhook("payment_intent.succeeded", order.pk)
        self.assertEqual(response.status_code, 200)

    def test_webhook_payment_succeeded_deducts_stock(self):
        product = _make_product(stock=10)
        order = _make_order(status="pending")
        OrderItem.objects.create(order=order, product=product, quantity=3, unit_price=product.price)

        self._post_webhook("payment_intent.succeeded", order.pk)

        product.refresh_from_db()
        self.assertEqual(product.stock, 7)

    def test_webhook_does_not_double_deduct_stock_for_already_paid_order(self):
        product = _make_product(stock=10)
        order = _make_order(status="paid")
        OrderItem.objects.create(order=order, product=product, quantity=3, unit_price=product.price)

        self._post_webhook("payment_intent.succeeded", order.pk)

        product.refresh_from_db()
        self.assertEqual(product.stock, 10)

    def test_webhook_stock_deduction_never_goes_negative(self):
        product = _make_product(stock=2)
        order = _make_order(status="pending")
        OrderItem.objects.create(order=order, product=product, quantity=5, unit_price=product.price)

        self._post_webhook("payment_intent.succeeded", order.pk)

        product.refresh_from_db()
        self.assertEqual(product.stock, 0)

    def test_webhook_invalid_signature_returns_400(self):
        with patch(
            "checkout.views.stripe.Webhook.construct_event",
            side_effect=__import__("stripe").error.SignatureVerificationError("bad sig", "t=1"),
        ):
            response = self.client.post(
                reverse("stripe_webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="bad",
            )
        self.assertEqual(response.status_code, 400)

    def test_webhook_unknown_event_type_returns_200(self):
        order = _make_order()
        response = self._post_webhook("customer.created", order.pk)
        self.assertEqual(response.status_code, 200)
