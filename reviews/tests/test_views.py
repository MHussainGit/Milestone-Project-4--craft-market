"""
Reviews view tests.

Run with: pytest reviews/tests/test_views.py -v
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from reviews.models import Review
from store.models import Product, Shop

User = get_user_model()


def _make_product(title="Test Bowl"):
    user = User.objects.create_user(f"maker_{User.objects.count()}", password="pass")
    shop = Shop.objects.create(name=f"Shop {user.username}", user=user)
    return Product.objects.create(title=title, shop=shop, price=Decimal("25.00"), stock=5)


def _make_review(product, user, rating=4):
    return Review.objects.create(
        product=product,
        user=user,
        rating=rating,
        headline="Great product",
        body="This is a thorough review with enough content to pass validation.",
    )


class ReviewCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("reviewer", password="pass")
        self.product = _make_product()

    def test_review_create_requires_login(self):
        response = self.client.get(reverse("review_create", kwargs={"product_slug": self.product.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_review_create_returns_200_for_authenticated(self):
        self.client.login(username="reviewer", password="pass")
        response = self.client.get(reverse("review_create", kwargs={"product_slug": self.product.slug}))
        self.assertEqual(response.status_code, 200)

    def test_review_create_post_creates_review(self):
        self.client.login(username="reviewer", password="pass")
        count_before = Review.objects.count()
        self.client.post(reverse("review_create", kwargs={"product_slug": self.product.slug}), {
            "rating": 5,
            "headline": "Excellent craft",
            "body": "This is a very thorough review with plenty of content for the reader.",
        })
        self.assertEqual(Review.objects.count(), count_before + 1)

    def test_second_review_for_same_product_redirects(self):
        self.client.login(username="reviewer", password="pass")
        _make_review(self.product, self.user)
        response = self.client.get(reverse("review_create", kwargs={"product_slug": self.product.slug}))
        self.assertRedirects(response, reverse("product_detail", kwargs={"slug": self.product.slug}))


class ReviewEditDeleteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user("owner", password="pass")
        self.other = User.objects.create_user("other", password="pass")
        self.product = _make_product("Edit Bowl")
        self.review = _make_review(self.product, self.owner)

    def test_review_edit_200_for_owner(self):
        self.client.login(username="owner", password="pass")
        response = self.client.get(reverse("review_edit", kwargs={"pk": self.review.pk}))
        self.assertEqual(response.status_code, 200)

    def test_review_edit_404_for_other_user(self):
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("review_edit", kwargs={"pk": self.review.pk}))
        self.assertEqual(response.status_code, 404)

    def test_review_delete_200_for_owner(self):
        self.client.login(username="owner", password="pass")
        response = self.client.get(reverse("review_delete", kwargs={"pk": self.review.pk}))
        self.assertEqual(response.status_code, 200)

    def test_review_delete_404_for_other_user(self):
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("review_delete", kwargs={"pk": self.review.pk}))
        self.assertEqual(response.status_code, 404)

    def test_review_delete_post_removes_review(self):
        self.client.login(username="owner", password="pass")
        pk = self.review.pk
        self.client.post(reverse("review_delete", kwargs={"pk": pk}))
        self.assertFalse(Review.objects.filter(pk=pk).exists())

    def test_review_edit_by_other_user_cannot_update(self):
        self.client.login(username="other", password="pass")
        response = self.client.post(reverse("review_edit", kwargs={"pk": self.review.pk}), {
            "rating": 1,
            "headline": "Hacked headline",
            "body": "This is an attempt to edit someone else's review.",
        })
        self.assertEqual(response.status_code, 404)
        self.review.refresh_from_db()
        self.assertEqual(self.review.headline, "Great product")
