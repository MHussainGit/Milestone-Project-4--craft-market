from django.urls import path

from . import views

urlpatterns = [
    path("", views.checkout_view, name="checkout"),
    path("create-payment-intent/", views.create_payment_intent, name="create_payment_intent"),
    path("success/<int:order_pk>/", views.checkout_success, name="checkout_success"),
    path("cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
]
