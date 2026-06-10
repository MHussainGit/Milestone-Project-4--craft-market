"""
Checkout model tests — Order, OrderItem.

Run with: pytest checkout/tests/test_models.py -v
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from store.models import Product, Shop

User = get_user_model()


def _make_product(title="Test Product", price="20.00", stock=5):
    user = User.objects.create_user(f"maker_{User.objects.count()}", password="pass")
    shop = Shop.objects.create(name=f"Shop {user.username}", user=user)
    return Product.objects.create(title=title, shop=shop, price=Decimal(price), stock=stock)


def _make_order(user=None, status="pending"):
    from checkout.models import Order
    return Order.objects.create(
        user=user,
        full_name="Jane Smith",
        email="jane@example.com",
        address_line1="1 Craft Lane",
        city="Makerville",
        postcode="MA1 1KE",
        status=status,
    )


class OrderModelTests(TestCase):

    def test_str_returns_expected_format(self):
        from checkout.models import Order
        order = _make_order(status="pending")
        self.assertIn("Order #", str(order))
        self.assertIn("Jane Smith", str(order))
        self.assertIn("pending", str(order))

    def test_get_total_sums_line_items(self):
        from checkout.models import Order, OrderItem
        order = _make_order()
        p1 = _make_product("Bowl", "10.00")
        p2 = _make_product("Mug", "5.00")
        OrderItem.objects.create(order=order, product=p1, quantity=2, unit_price=Decimal("10.00"))
        OrderItem.objects.create(order=order, product=p2, quantity=1, unit_price=Decimal("5.00"))
        self.assertEqual(order.get_total(), Decimal("25.00"))

    def test_get_total_empty_order_is_zero(self):
        order = _make_order()
        self.assertEqual(order.get_total(), Decimal("0.00"))

    def test_get_total_pence_is_integer(self):
        from checkout.models import OrderItem
        order = _make_order()
        product = _make_product("Ring", "9.99")
        OrderItem.objects.create(order=order, product=product, quantity=1, unit_price=Decimal("9.99"))
        pence = order.get_total_pence()
        self.assertIsInstance(pence, int)
        self.assertEqual(pence, 999)

    def test_item_count_sums_quantities(self):
        from checkout.models import OrderItem
        order = _make_order()
        p1 = _make_product("Vase", "15.00")
        p2 = _make_product("Candle", "8.00")
        OrderItem.objects.create(order=order, product=p1, quantity=3, unit_price=Decimal("15.00"))
        OrderItem.objects.create(order=order, product=p2, quantity=2, unit_price=Decimal("8.00"))
        self.assertEqual(order.item_count(), 5)

    def test_ordering_is_by_created_at_descending(self):
        from checkout.models import Order
        o1 = _make_order()
        o2 = _make_order()
        orders = list(Order.objects.all())
        self.assertEqual(orders[0], o2)
        self.assertEqual(orders[1], o1)


class OrderItemModelTests(TestCase):

    def test_str_returns_quantity_and_title(self):
        from checkout.models import OrderItem
        order = _make_order()
        product = _make_product("Ceramic Jug", "30.00")
        item = OrderItem.objects.create(order=order, product=product, quantity=3, unit_price=Decimal("30.00"))
        self.assertIn("3", str(item))
        self.assertIn("Ceramic Jug", str(item))

    def test_get_line_total_multiplies_price_by_quantity(self):
        from checkout.models import OrderItem
        order = _make_order()
        product = _make_product("Bracelet", "8.00")
        item = OrderItem.objects.create(order=order, product=product, quantity=4, unit_price=Decimal("8.00"))
        self.assertEqual(item.get_line_total(), Decimal("32.00"))
