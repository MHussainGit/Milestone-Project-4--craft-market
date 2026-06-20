"""
CraftMarket – root URL configuration.

Each Django app owns its own urls.py and is included here with a
consistent prefix.  URL names are defined in each app and referenced
with {% url 'name' %} in templates.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    # PWA: manifest, root-scoped service worker, and offline fallback page.
    # The service worker is served from the site root so its scope covers
    # every page (a /static/ path would limit it to /static/).
    path(
        "manifest.webmanifest",
        TemplateView.as_view(
            template_name="pwa/manifest.webmanifest",
            content_type="application/manifest+json",
        ),
        name="manifest",
    ),
    path(
        "service-worker.js",
        TemplateView.as_view(
            template_name="pwa/service-worker.js",
            content_type="application/javascript",
        ),
        name="service_worker",
    ),
    path(
        "offline/",
        TemplateView.as_view(template_name="pwa/offline.html"),
        name="offline",
    ),
    path("", include("store.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
    path("accounts/", include("accounts.urls")),
    path("reviews/", include("reviews.urls")),
]
