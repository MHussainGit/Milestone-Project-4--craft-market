from decimal import Decimal

from store.models import Product


def get_cart_items_from_session(session) -> list:
    """
    Fetch Product objects for each key in session['cart'].

    Returns a list of dicts:
        [{'product': Product, 'quantity': int, 'line_total': Decimal}, ...]

    Silently skips any cart entries whose Product no longer exists.
    """
    cart = session.get("cart", {})
    if not cart:
        return []

    product_pks = [int(pk) for pk in cart.keys()]
    products_by_pk = {p.pk: p for p in Product.objects.filter(pk__in=product_pks)}

    items = []
    for pk_str, quantity in cart.items():
        product = products_by_pk.get(int(pk_str))
        if product:
            line_total = product.price * quantity
            items.append({"product": product, "quantity": quantity, "line_total": line_total})
    return items


def get_cart_total(cart_items: list) -> Decimal:
    return sum((item["line_total"] for item in cart_items), Decimal("0.00"))


def clear_cart(session) -> None:
    session.pop("cart", None)
