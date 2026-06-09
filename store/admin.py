from django.contrib import admin

from .models import Category, Product, Shop


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "location", "created_at"]
    search_fields = ["name", "user__username"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "shop", "category", "price", "stock", "featured", "made_to_order"]
    list_filter = ["category", "featured", "made_to_order"]
    search_fields = ["title", "shop__name", "materials"]
    list_editable = ["price", "stock", "featured"]
    prepopulated_fields = {"slug": ("title",)}
