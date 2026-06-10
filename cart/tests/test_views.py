"""
Cart view tests.

Run with: pytest cart/tests/test_views.py -v
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from store.models import Product, Shop

User = get_user_model()


def _make_product(title="Test Bowl", stock=10, price="25.00"):
    user = User.objects.create_user(f"maker_{User.objects.count()}", password="pass")
    shop = Shop.objects.create(name=f"Shop {user.username}", user=user)
    return Product.objects.create(title=title, shop=shop, price=Decimal(price), stock=stock)


class CartViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = _make_product()

    def test_cart_detail_returns_200(self):
        response = self.client.get(reverse("cart_detail"))
        self.assertEqual(response.status_code, 200)

    def test_cart_add_post_sets_session(self):
        self.client.post(reverse("cart_add", kwargs={"product_pk": self.product.pk}), {
            "quantity": 2,
            "override": "",
        })
        cart = self.client.session.get("cart", {})
        self.assertIn(str(self.product.pk), cart)
        self.assertEqual(cart[str(self.product.pk)], 2)

    def test_cart_add_accumulates_quantity(self):
        self.client.post(reverse("cart_add", kwargs={"product_pk": self.product.pk}), {
            "quantity": 1, "override": "",
        })
        self.client.post(reverse("cart_add", kwargs={"product_pk": self.product.pk}), {
            "quantity": 2, "override": "",
        })
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[str(self.product.pk)], 3)

    def test_cart_add_redirects_to_cart(self):
        response = self.client.post(reverse("cart_add", kwargs={"product_pk": self.product.pk}), {
            "quantity": 1, "override": "",
        })
        self.assertRedirects(response, reverse("cart_detail"))

    def test_cart_remove_post_removes_item(self):
        self.client.post(reverse("cart_add", kwargs={"product_pk": self.product.pk}), {
            "quantity": 1, "override": "",
        })
        self.client.post(reverse("cart_remove", kwargs={"product_pk": self.product.pk}))
        cart = self.client.session.get("cart", {})
        self.assertNotIn(str(self.product.pk), cart)

    def test_cart_update_post_changes_quantity(self):
        self.client.post(reverse("cart_add", kwargs={"product_pk": self.product.pk}), {
            "quantity": 1, "override": "",
        })
        self.client.post(reverse("cart_update", kwargs={"product_pk": self.product.pk}), {
            "quantity": 5, "override": True,
        })
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[str(self.product.pk)], 5)

    def test_cart_shows_item_after_add(self):
        self.client.post(reverse("cart_add", kwargs={"product_pk": self.product.pk}), {
            "quantity": 1, "override": "",
        })
        response = self.client.get(reverse("cart_detail"))
        self.assertContains(response, self.product.title)

    def test_cart_add_exceeds_stock_capped(self):
        self.client.post(reverse("cart_add", kwargs={"product_pk": self.product.pk}), {
            "quantity": 999, "override": "",
        })
        cart = self.client.session.get("cart", {})
        qty = cart.get(str(self.product.pk), 0)
        self.assertLessEqual(qty, self.product.stock)
