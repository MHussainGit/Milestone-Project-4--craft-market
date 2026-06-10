from django.urls import path

from . import views

urlpatterns = [
    path("product/<slug:product_slug>/create/", views.review_create, name="review_create"),
    path("<int:pk>/edit/", views.ReviewUpdateView.as_view(), name="review_edit"),
    path("<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
]
