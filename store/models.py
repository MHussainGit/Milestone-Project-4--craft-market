from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.utils.text import slugify

User = get_user_model()


def _resolve_image_src(image_url):
    """Resolve a stored image reference to a usable ``src`` URL.

    External (``http(s)://``) and root-relative (``/``) values are returned
    unchanged; everything else is treated as a path under ``STATIC_URL`` and
    resolved via ``static()`` so it works with hashed/manifest storage.
    """
    if not image_url:
        return ""
    if image_url.startswith(("http://", "https://", "/")):
        return image_url
    return static(image_url)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="shop")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    image_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def image_src(self):
        return _resolve_image_src(self.image_url)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Shop.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductQuerySet(models.QuerySet):
    def featured(self):
        return self.filter(featured=True)

    def in_stock(self):
        return self.filter(stock__gt=0)


class Product(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    description = models.TextField(blank=True)
    materials = models.CharField(max_length=300, blank=True)
    made_to_order = models.BooleanField(default=False)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    stock = models.PositiveIntegerField(default=0)
    image_url = models.CharField(max_length=500, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def image_src(self):
        return _resolve_image_src(self.image_url)

    def is_in_stock(self):
        return self.stock > 0

    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)
