"""
Cart context processor.

Injects `cart_item_count` into every template context so the navbar
can display the current number of items without each view needing to
pass it explicitly.
"""


def cart_item_count(request):
    """Return total quantity of all items in the session cart."""
    cart = request.session.get("cart", {})
    count = sum(cart.values())
    return {"cart_item_count": count}
