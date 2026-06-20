import json
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import F
from django.db.models.functions import Greatest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.utils import clear_cart, get_cart_items_from_session, get_cart_total
from store.models import Product

from .forms import ShippingForm
from .models import Order, OrderItem

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout_view(request):
    cart_items = get_cart_items_from_session(request.session)
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart_detail")

    total = get_cart_total(cart_items)

    initial = {}
    last_order = Order.objects.filter(user=request.user).order_by("-created_at").first()
    if last_order:
        initial = {
            "full_name": last_order.full_name,
            "email": last_order.email,
            "address_line1": last_order.address_line1,
            "address_line2": last_order.address_line2,
            "city": last_order.city,
            "postcode": last_order.postcode,
            "country": last_order.country,
        }

    form = ShippingForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        order = form.save(commit=False)
        order.user = request.user
        order.status = "pending"
        order.save()
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                unit_price=item["product"].price,
            )
        request.session["pending_order_pk"] = order.pk
        return render(request, "checkout/checkout.html", {
            "form": form,
            "cart_items": cart_items,
            "total": total,
            "order": order,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "payment_step": True,
        })

    return render(request, "checkout/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "total": total,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "payment_step": False,
    })


@login_required
@require_POST
def create_payment_intent(request):
    try:
        data = json.loads(request.body)
        order_pk = data.get("order_pk") or request.session.get("pending_order_pk")
        order = get_object_or_404(Order, pk=order_pk, user=request.user)
        intent = stripe.PaymentIntent.create(
            amount=order.get_total_pence(),
            currency="gbp",
            metadata={"order_pk": order.pk},
        )
        order.stripe_payment_intent_id = intent.id
        order.save(update_fields=["stripe_payment_intent_id"])
        return JsonResponse({"client_secret": intent.client_secret})
    except Exception as exc:
        logger.exception("PaymentIntent creation failed: %s", exc)
        return JsonResponse({"error": str(exc)}, status=400)


def _deduct_stock(order):
    for item in order.items.values("product_id", "quantity"):
        Product.objects.filter(pk=item["product_id"]).update(
            stock=Greatest(F("stock") - item["quantity"], 0)
        )


def _mark_order_paid(order):
    """
    Atomically transition the order from pending to paid and deduct stock.

    The status filter makes this safe to call from both checkout_success and
    the Stripe webhook — only the request that wins the pending->paid update
    deducts stock, so a paid order is never double-deducted.
    """
    updated = Order.objects.filter(pk=order.pk, status="pending").update(status="paid")
    if updated:
        order.status = "paid"
        _deduct_stock(order)
    return bool(updated)


def _record_card_details(order):
    """
    Fetch the card brand and last 4 digits from Stripe for display on the
    receipt. Only this non-sensitive metadata is stored — the full card
    number and CVC never reach the Django application or database.
    """
    if not order.stripe_payment_intent_id or order.card_last4:
        return
    try:
        intent = stripe.PaymentIntent.retrieve(
            order.stripe_payment_intent_id, expand=["payment_method"]
        )
        card = intent.payment_method.card
        order.card_brand = card.brand
        order.card_last4 = card.last4
        order.save(update_fields=["card_brand", "card_last4"])
    except Exception:
        logger.exception("Failed to fetch card details for order %s", order.pk)


@login_required
def checkout_success(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, user=request.user)
    # Send the confirmation email from whichever path wins the pending->paid
    # transition (this success page or the Stripe webhook). _mark_order_paid is
    # atomic, so only the winner returns True — the email goes out exactly once.
    if _mark_order_paid(order):
        _send_order_confirmation(order)
    _record_card_details(order)
    clear_cart(request.session)
    return render(request, "checkout/success.html", {"order": order})


@login_required
def checkout_cancel(request):
    return render(request, "checkout/cancel.html")


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook signature verification failed.")
        return HttpResponse(status=400)
    except ValueError:
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order_pk = intent.get("metadata", {}).get("order_pk")
        if order_pk:
            try:
                order = Order.objects.get(pk=order_pk)
                if _mark_order_paid(order):
                    _send_order_confirmation(order)
                _record_card_details(order)
            except Order.DoesNotExist:
                logger.error("Webhook: Order %s not found.", order_pk)

    return HttpResponse(status=200)


def _send_order_confirmation(order):
    subject = f"CraftMarket — Order #{order.pk} confirmed"
    items_text = "\n".join(
        f"  {item.quantity}× {item.product.title} — £{item.get_line_total():.2f}"
        for item in order.items.select_related("product").all()
    )
    body = (
        f"Hi {order.full_name},\n\n"
        f"Thank you for your order!\n\n"
        f"Order #{order.pk}\n"
        f"{'─' * 30}\n"
        f"{items_text}\n"
        f"{'─' * 30}\n"
        f"Total: £{order.get_total():.2f}\n\n"
        f"Your handmade items will be dispatched soon.\n\n"
        f"— The CraftMarket Team"
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [order.email], fail_silently=True)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "checkout/order_list.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "checkout/order_detail.html", {"order": order})


@login_required
def order_resume(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user, status="pending")
    request.session["pending_order_pk"] = order.pk
    cart_items = [
        {"product": item.product, "quantity": item.quantity, "line_total": item.get_line_total()}
        for item in order.items.select_related("product")
    ]
    return render(request, "checkout/checkout.html", {
        "cart_items": cart_items,
        "total": order.get_total(),
        "order": order,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "payment_step": True,
    })


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user, status="pending")
    if request.method == "POST":
        order.delete()
        messages.success(request, f"Order #{pk} was deleted.")
        return redirect("order_list")
    return render(request, "confirm_delete.html", {
        "object_name": f"Order #{order.pk}",
        "cancel_url": reverse("order_list"),
    })
