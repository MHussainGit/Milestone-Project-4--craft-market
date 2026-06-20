"""
Checkout view tests.

Run with: pytest checkout/tests/test_views.py -v
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from checkout.models import Order, OrderItem
from store.models import Product, Shop

User = get_user_model()


def _make_product(title="Test Bowl", stock=5, price="25.00"):
    user = User.objects.create_user(f"maker_{User.objects.count()}", password="pass")
    shop = Shop.objects.create(name=f"Shop {user.username}", user=user)
    return Product.objects.create(title=title, shop=shop, price=Decimal(price), stock=stock)


def _make_order(user, status="paid"):
    return Order.objects.create(
        user=user,
        full_name="Test User",
        email="test@example.com",
        address_line1="1 Craft St",
        city="Makerville",
        postcode="MA1 1KE",
        status=status,
    )


class CheckoutAccessTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_checkout_redirects_anonymous(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_order_list_redirects_anonymous(self):
        response = self.client.get(reverse("order_list"))
        self.assertEqual(response.status_code, 302)

    def test_checkout_cancel_redirects_anonymous(self):
        response = self.client.get(reverse("checkout_cancel"))
        self.assertEqual(response.status_code, 302)


class CheckoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("checkoutuser", password="pass")
        self.product = _make_product()

    def test_checkout_redirects_to_cart_when_empty(self):
        self.client.login(username="checkoutuser", password="pass")
        response = self.client.get(reverse("checkout"))
        self.assertRedirects(response, reverse("cart_detail"))

    def test_checkout_returns_200_with_items_in_cart(self):
        self.client.login(username="checkoutuser", password="pass")
        session = self.client.session
        session["cart"] = {str(self.product.pk): 1}
        session.save()
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 200)

    def test_checkout_post_creates_order(self):
        self.client.login(username="checkoutuser", password="pass")
        session = self.client.session
        session["cart"] = {str(self.product.pk): 1}
        session.save()
        count_before = Order.objects.count()
        self.client.post(reverse("checkout"), {
            "full_name": "Jane Smith",
            "email": "jane@example.com",
            "address_line1": "1 Craft Lane",
            "address_line2": "",
            "city": "Makerville",
            "postcode": "MA1 1KE",
            "country": "United Kingdom",
        })
        self.assertGreater(Order.objects.count(), count_before)

    def test_checkout_cancel_returns_200(self):
        self.client.login(username="checkoutuser", password="pass")
        response = self.client.get(reverse("checkout_cancel"))
        self.assertEqual(response.status_code, 200)


class CheckoutSuccessEmailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "buyer", password="pass", email="buyer@example.com"
        )
        self.product = _make_product()

    def _pending_order(self):
        order = Order.objects.create(
            user=self.user, full_name="Buyer", email="buyer@example.com",
            address_line1="1 Craft St", city="Makerville", postcode="MA1 1KE",
            status="pending",
        )
        OrderItem.objects.create(
            order=order, product=self.product, quantity=1,
            unit_price=self.product.price,
        )
        return order

    def test_success_page_sends_confirmation_email(self):
        order = self._pending_order()
        self.client.login(username="buyer", password="pass")
        mail.outbox = []
        self.client.get(reverse("checkout_success", kwargs={"order_pk": order.pk}))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(order.email, mail.outbox[0].to)
        self.assertIn(f"#{order.pk}", mail.outbox[0].subject)

    def test_success_page_marks_order_paid(self):
        order = self._pending_order()
        self.client.login(username="buyer", password="pass")
        self.client.get(reverse("checkout_success", kwargs={"order_pk": order.pk}))
        order.refresh_from_db()
        self.assertEqual(order.status, "paid")

    def test_already_paid_order_does_not_resend_email(self):
        order = self._pending_order()
        order.status = "paid"
        order.save()
        self.client.login(username="buyer", password="pass")
        mail.outbox = []
        self.client.get(reverse("checkout_success", kwargs={"order_pk": order.pk}))
        self.assertEqual(len(mail.outbox), 0)


class OrderListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user("user1", password="pass")
        self.user2 = User.objects.create_user("user2", password="pass")
        self.order1 = _make_order(self.user1)
        self.order2 = _make_order(self.user2)

    def test_order_list_shows_only_own_orders(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("order_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"#{self.order1.pk}")
        self.assertNotContains(response, f"#{self.order2.pk}")

    def test_order_detail_404_for_other_users_order(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("order_detail", kwargs={"pk": self.order2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_order_detail_200_for_own_order(self):
        self.client.login(username="user1", password="pass")
        response = self.client.get(reverse("order_detail", kwargs={"pk": self.order1.pk}))
        self.assertEqual(response.status_code, 200)
