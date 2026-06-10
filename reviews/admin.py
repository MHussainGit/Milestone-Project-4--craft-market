from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "rating", "headline", "created_at"]
    list_filter = ["rating"]
    search_fields = ["product__title", "user__username", "headline"]
