"""
Store view tests — public browsing and shop owner CRUD.

Run with: pytest store/tests/test_views.py -v
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from store.models import Category, Product, Shop

User = get_user_model()


def _make_user(username="testmaker", password="pass"):
    return User.objects.create_user(username, password=password)


def _make_shop(user, name="Test Shop"):
    return Shop.objects.create(name=name, user=user)


def _make_category(name="Ceramics"):
    return Category.objects.create(name=name)


def _make_product(title="Test Bowl", price="25.00", stock=5, featured=False, shop=None, category=None):
    if shop is None:
        user = _make_user(f"auto_{User.objects.count()}")
        shop = _make_shop(user)
    return Product.objects.create(
        title=title,
        shop=shop,
        price=Decimal(price),
        stock=stock,
        featured=featured,
        category=category,
    )


class PublicStoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.shop = _make_shop(self.user)
        self.category = _make_category()
        self.product = _make_product(shop=self.shop, category=self.category)

    def test_home_returns_200(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_product_list_returns_200(self):
        response = self.client.get(reverse("product_list"))
        self.assertEqual(response.status_code, 200)

    def test_product_list_shows_products(self):
        response = self.client.get(reverse("product_list"))
        self.assertContains(response, self.product.title)

    def test_product_detail_returns_200(self):
        response = self.client.get(reverse("product_detail", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 200)

    def test_product_detail_shows_title(self):
        response = self.client.get(reverse("product_detail", kwargs={"slug": self.product.slug}))
        self.assertContains(response, self.product.title)

    def test_product_detail_404_for_unknown_slug(self):
        response = self.client.get(reverse("product_detail", kwargs={"slug": "no-such-product"}))
        self.assertEqual(response.status_code, 404)

    def test_product_search_returns_200(self):
        response = self.client.get(reverse("product_search") + "?q=Test")
        self.assertEqual(response.status_code, 200)

    def test_product_search_shows_matching_products(self):
        response = self.client.get(reverse("product_search") + "?q=Test")
        self.assertContains(response, self.product.title)

    def test_product_search_no_results_for_unknown_query(self):
        response = self.client.get(reverse("product_search") + "?q=zzznomatch")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.product.title)

    def test_category_detail_returns_200(self):
        response = self.client.get(reverse("category_detail", kwargs={"slug": self.category.slug}))
        self.assertEqual(response.status_code, 200)

    def test_category_detail_shows_products(self):
        response = self.client.get(reverse("category_detail", kwargs={"slug": self.category.slug}))
        self.assertContains(response, self.product.title)

    def test_shop_detail_returns_200(self):
        response = self.client.get(reverse("shop_detail", kwargs={"slug": self.shop.slug}))
        self.assertEqual(response.status_code, 200)

    def test_home_shows_featured_products(self):
        _make_product(title="Featured Vase!", featured=True, shop=self.shop)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Featured Vase!")


class ShopOwnerCrudTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = _make_user("owner")
        self.other = _make_user("other")
        self.shop = _make_shop(self.owner)
        self.category = _make_category()
        self.product = _make_product(shop=self.shop, category=self.category)

    def test_product_create_redirects_anonymous(self):
        response = self.client.get(reverse("product_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_product_create_403_for_user_without_shop(self):
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("product_create"))
        self.assertEqual(response.status_code, 403)

    def test_product_create_200_for_shop_owner(self):
        self.client.login(username="owner", password="pass")
        response = self.client.get(reverse("product_create"))
        self.assertEqual(response.status_code, 200)

    def test_product_create_post_creates_product(self):
        self.client.login(username="owner", password="pass")
        count_before = Product.objects.count()
        self.client.post(reverse("product_create"), {
            "title": "New Candle",
            "price": "12.99",
            "stock": 10,
            "description": "",
            "materials": "beeswax, cotton",
            "made_to_order": False,
            "image_url": "",
            "featured": False,
        })
        self.assertEqual(Product.objects.count(), count_before + 1)
        self.assertTrue(Product.objects.filter(title="New Candle").exists())

    def test_product_edit_200_for_owner(self):
        self.client.login(username="owner", password="pass")
        response = self.client.get(reverse("product_edit", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 200)

    def test_product_edit_403_for_other_user(self):
        # Give other user a shop so they pass the login check but not the owner check
        other_shop = _make_shop(self.other, name="Other Shop")
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("product_edit", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 403)

    def test_product_delete_post_deletes_product(self):
        self.client.login(username="owner", password="pass")
        pk = self.product.pk
        self.client.post(reverse("product_delete", kwargs={"slug": self.product.slug}))
        self.assertFalse(Product.objects.filter(pk=pk).exists())

    def test_product_delete_403_for_other_user(self):
        _make_shop(self.other, name="Other Shop")
        self.client.login(username="other", password="pass")
        response = self.client.post(reverse("product_delete", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 403)
