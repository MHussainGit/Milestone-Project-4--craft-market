"""
PageTurner – root URL configuration.

Each Django app owns its own urls.py and is included here with a
consistent prefix.  URL names are defined in each app and referenced
with {% url 'name' %} in templates.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("store.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
    path("accounts/", include("accounts.urls")),
    path("reviews/", include("reviews.urls")),
]
