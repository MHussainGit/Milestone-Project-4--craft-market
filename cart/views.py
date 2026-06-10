from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from store.models import Product

from .forms import CartAddForm
from .utils import clear_cart, get_cart_items_from_session, get_cart_total


def cart_detail(request):
    cart_items = get_cart_items_from_session(request.session)
    total = get_cart_total(cart_items)
    return render(request, "cart/cart_detail.html", {
        "cart_items": cart_items,
        "total": total,
    })


def cart_add(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = CartAddForm(request.POST or None, max_stock=product.stock)
    if request.method == "POST" and form.is_valid():
        quantity = form.cleaned_data["quantity"]
        override = form.cleaned_data["override"]
        cart = request.session.get("cart", {})
        key = str(product_pk)
        if override:
            cart[key] = quantity
        else:
            cart[key] = cart.get(key, 0) + quantity
            if cart[key] > product.stock:
                cart[key] = product.stock
        request.session["cart"] = cart
        messages.success(request, f"'{product.title}' added to your cart.")
    return redirect("cart_detail")


def cart_update(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    form = CartAddForm(request.POST or None, max_stock=product.stock)
    if request.method == "POST" and form.is_valid():
        quantity = form.cleaned_data["quantity"]
        cart = request.session.get("cart", {})
        cart[str(product_pk)] = quantity
        request.session["cart"] = cart
    return redirect("cart_detail")


def cart_remove(request, product_pk):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        cart.pop(str(product_pk), None)
        request.session["cart"] = cart
        messages.info(request, "Item removed from your cart.")
    return redirect("cart_detail")
