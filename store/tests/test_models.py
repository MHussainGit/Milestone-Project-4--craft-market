"""
Store model tests.

Run with: pytest store/tests/test_models.py -v
"""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class CategoryModelTests(TestCase):
    def _make_category(self, name="Ceramics", description=""):
        from store.models import Category
        return Category.objects.create(name=name, description=description)

    def test_str_returns_name(self):
        cat = self._make_category("Textiles")
        self.assertEqual(str(cat), "Textiles")

    def test_slug_auto_generated_on_save(self):
        cat = self._make_category("Leather Goods")
        self.assertEqual(cat.slug, "leather-goods")

    def test_slug_unique_constraint(self):
        self._make_category("Jewellery")
        with self.assertRaises(Exception):
            self._make_category("Jewellery")

    def test_ordering_is_by_name(self):
        from store.models import Category
        self._make_category("Woodwork")
        self._make_category("Ceramics")
        names = list(Category.objects.values_list("name", flat=True))
        self.assertEqual(names, sorted(names))


class ShopModelTests(TestCase):
    def _make_user(self, username="maker1"):
        return User.objects.create_user(username, password="pass")

    def _make_shop(self, name="The Clay Studio", user=None):
        from store.models import Shop
        if user is None:
            user = self._make_user()
        return Shop.objects.create(name=name, user=user)

    def test_str_returns_name(self):
        shop = self._make_shop("Woodland Craft")
        self.assertEqual(str(shop), "Woodland Craft")

    def test_slug_auto_generated_on_save(self):
        shop = self._make_shop("The Clay Studio")
        self.assertIn("the-clay-studio", shop.slug)

    def test_ordering_is_by_name(self):
        from store.models import Shop
        u1 = self._make_user("u1")
        u2 = self._make_user("u2")
        Shop.objects.create(name="Zelda's Weave", user=u1)
        Shop.objects.create(name="Amber Forge", user=u2)
        names = list(Shop.objects.values_list("name", flat=True))
        self.assertEqual(names, sorted(names))


class ProductModelTests(TestCase):
    def _make_shop(self):
        from store.models import Shop
        user = User.objects.create_user(f"maker_{User.objects.count()}", password="pass")
        return Shop.objects.create(name=f"Shop {user.username}", user=user)

    def _make_product(self, title="Oak Bowl", price="35.00", stock=5):
        from store.models import Product
        shop = self._make_shop()
        return Product.objects.create(
            title=title,
            shop=shop,
            price=Decimal(price),
            stock=stock,
        )

    def test_str_returns_title(self):
        product = self._make_product("Linen Tote")
        self.assertEqual(str(product), "Linen Tote")

    def test_slug_auto_generated_from_title(self):
        product = self._make_product("Hand-thrown Mug")
        self.assertIn("hand-thrown-mug", product.slug)

    def test_slug_is_unique(self):
        from store.models import Product
        shop = self._make_shop()
        Product.objects.create(title="Same Title", shop=shop, price=Decimal("10.00"), stock=1)
        product2 = Product.objects.create(title="Same Title", shop=shop, price=Decimal("10.00"), stock=1)
        self.assertNotEqual(product2.slug, "")

    def test_is_in_stock_true_when_stock_positive(self):
        product = self._make_product(stock=3)
        self.assertTrue(product.is_in_stock())

    def test_is_in_stock_false_when_stock_zero(self):
        product = self._make_product(stock=0)
        self.assertFalse(product.is_in_stock())

    def test_featured_defaults_to_false(self):
        product = self._make_product()
        self.assertFalse(product.featured)

    def test_made_to_order_defaults_to_false(self):
        product = self._make_product()
        self.assertFalse(product.made_to_order)

    def test_product_queryset_featured_filter(self):
        from store.models import Product
        shop = self._make_shop()
        Product.objects.create(title="Featured Item", shop=shop, price=Decimal("20.00"), stock=1, featured=True)
        Product.objects.create(title="Normal Item",   shop=shop, price=Decimal("20.00"), stock=1, featured=False)
        featured = Product.objects.featured()
        self.assertEqual(featured.count(), 1)
        self.assertEqual(featured.first().title, "Featured Item")

    def test_product_queryset_in_stock_filter(self):
        from store.models import Product
        shop = self._make_shop()
        Product.objects.create(title="In Stock",  shop=shop, price=Decimal("20.00"), stock=3)
        Product.objects.create(title="Out Stock", shop=shop, price=Decimal("20.00"), stock=0)
        in_stock = Product.objects.in_stock()
        self.assertEqual(in_stock.count(), 1)
        self.assertEqual(in_stock.first().title, "In Stock")

    def test_average_rating_returns_none_with_no_reviews(self):
        product = self._make_product()
        self.assertIsNone(product.average_rating())

    def test_ordering_is_by_title(self):
        from store.models import Product
        shop = self._make_shop()
        Product.objects.create(title="Zebra Pot", shop=shop, price=Decimal("20.00"), stock=1)
        Product.objects.create(title="Apple Ring", shop=shop, price=Decimal("20.00"), stock=1)
        titles = list(Product.objects.values_list("title", flat=True))
        self.assertEqual(titles, sorted(titles))
