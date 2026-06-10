"""
Management command to seed the database with initial artisan shop and product data.

Usage:
    python manage.py seed_products

Safe to run multiple times — uses get_or_create so existing records are not duplicated.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from store.models import Category, Product, Shop

User = get_user_model()


CATEGORIES = [
    ("Ceramics", "Handthrown and handbuilt pottery, tiles, and decorative ware."),
    ("Jewellery", "Handcrafted rings, necklaces, bracelets, and earrings."),
    ("Textiles", "Woven, knitted, and printed fabrics, scarves, and homewares."),
    ("Woodwork", "Hand-carved and turned wooden objects, furniture, and gifts."),
    ("Leather Goods", "Hand-stitched wallets, bags, belts, and accessories."),
]

# (shop_username, shop_name, shop_description, shop_location)
SHOPS = [
    ("claystudio", "The Clay Studio", "Handthrown stoneware inspired by the natural landscape.", "Bristol, UK"),
    ("woodlandcraft", "Woodland Craft Co.", "Sustainably sourced woodwork made in a forest workshop.", "Dorset, UK"),
    ("theweave", "The Weave", "Natural fibre textiles: linen, cotton, and wool.", "Edinburgh, UK"),
    ("amberforge", "Amber Forge", "Contemporary silver and gold jewellery with gemstone accents.", "London, UK"),
    ("sewnleather", "Sewn & Leather", "Vegetable-tanned leather goods built to last a lifetime.", "York, UK"),
]

# (shop_username, title, category_name, price, stock, featured, image_url, description, materials, made_to_order)
PRODUCTS = [
    (
        "claystudio", "Handthrown Stoneware Mug", "Ceramics", "28.00", 12, True,
        "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=400",
        "A beautifully weighted everyday mug with a comfortable handle and subtle glaze variations.",
        "Stoneware clay, food-safe glaze", False,
    ),
    (
        "claystudio", "Speckled Cereal Bowl", "Ceramics", "32.00", 8, False,
        "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400",
        "Wide, shallow bowl ideal for cereal, salads, or soup. Each piece unique from the kiln.",
        "Stoneware clay, iron-speckle glaze", False,
    ),
    (
        "claystudio", "Bespoke Wedding Set (2 Mugs)", "Ceramics", "65.00", 0, False,
        "",
        "Personalised matching pair of mugs — names and wedding date carved before firing.",
        "Stoneware clay, satin glaze", True,
    ),
    (
        "woodlandcraft", "Turned Oak Salad Bowl", "Woodwork", "85.00", 4, True,
        "https://images.unsplash.com/photo-1604365888519-3a3bd4936e74?w=400",
        "Lathe-turned from a single piece of English oak, finished with food-safe oil.",
        "English oak, linseed oil", False,
    ),
    (
        "woodlandcraft", "Walnut Cheese Board", "Woodwork", "45.00", 7, False,
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
        "Hand-planed walnut serving board with a built-in juice groove.",
        "Black walnut, beeswax finish", False,
    ),
    (
        "woodlandcraft", "Carved Butter Spreader", "Woodwork", "14.00", 20, False,
        "",
        "Slim, ergonomic spreader carved by hand from cherry wood.",
        "Cherry wood", False,
    ),
    (
        "theweave", "Natural Linen Table Runner", "Textiles", "38.00", 6, True,
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400",
        "Undyed linen runner woven on a floor loom. Softens beautifully with every wash.",
        "100% linen", False,
    ),
    (
        "theweave", "Merino Wool Throw", "Textiles", "120.00", 3, True,
        "https://images.unsplash.com/photo-1584365685547-9a5fb6f3a70c?w=400",
        "Oversized throw woven in a herringbone pattern from undyed Merino wool.",
        "100% Merino wool", False,
    ),
    (
        "theweave", "Custom Monogram Cushion Cover", "Textiles", "55.00", 0, False,
        "",
        "Plain weave linen cushion cover with your initial woven in contrast thread.",
        "Linen, cotton thread", True,
    ),
    (
        "amberforge", "Sterling Silver Stacking Ring", "Jewellery", "48.00", 15, True,
        "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400",
        "Slim band hand-formed and hammered for a subtle organic texture.",
        "Sterling silver (.925)", False,
    ),
    (
        "amberforge", "Moonstone Drop Earrings", "Jewellery", "72.00", 6, True,
        "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400",
        "Delicate drops with a natural rainbow moonstone set in fine silver bezel.",
        "Fine silver, rainbow moonstone", False,
    ),
    (
        "amberforge", "Bespoke Engagement Ring", "Jewellery", "480.00", 0, False,
        "",
        "Fully bespoke design process: sketch, wax model approval, then cast in your choice of metal.",
        "9ct gold or sterling silver, stone of choice", True,
    ),
    (
        "sewnleather", "Slim Bifold Wallet", "Leather Goods", "55.00", 10, True,
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400",
        "Four card slots and a cash pocket, saddle-stitched for decades of use.",
        "Vegetable-tanned cow leather, linen thread", False,
    ),
    (
        "sewnleather", "Waxed Canvas Tote", "Leather Goods", "95.00", 5, False,
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400",
        "Heavy-duty tote with leather-reinforced handles and a magnetic snap closure.",
        "Waxed canvas, vegetable-tanned leather", False,
    ),
    (
        "sewnleather", "Personalised Luggage Tag", "Leather Goods", "22.00", 25, False,
        "",
        "Debossed with your initials (up to 3 characters) — a classic travel gift.",
        "Vegetable-tanned leather", True,
    ),
]


class Command(BaseCommand):
    help = "Seed the database with initial artisan shops and products."

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories…")
        categories = {}
        for name, description in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            categories[name] = cat
            if created:
                self.stdout.write(f"  Created category: {name}")

        self.stdout.write("Seeding shops…")
        shops = {}
        for username, shop_name, description, location in SHOPS:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@craftmarket.example"},
            )
            if _:
                user.set_password("craftmarket123")
                user.save()
            shop, created = Shop.objects.get_or_create(
                user=user,
                defaults={
                    "name": shop_name,
                    "description": description,
                    "location": location,
                },
            )
            shops[username] = shop
            if created:
                self.stdout.write(f"  Created shop: {shop_name}")

        self.stdout.write("Seeding products…")
        for (username, title, category_name, price, stock,
             featured, image_url, description, materials, made_to_order) in PRODUCTS:
            product, created = Product.objects.get_or_create(
                title=title,
                shop=shops[username],
                defaults={
                    "category": categories.get(category_name),
                    "price": price,
                    "stock": stock,
                    "featured": featured,
                    "image_url": image_url,
                    "description": description,
                    "materials": materials,
                    "made_to_order": made_to_order,
                },
            )
            if created:
                self.stdout.write(f"  Created product: {title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {Category.objects.count()} categories, "
                f"{Shop.objects.count()} shops, "
                f"{Product.objects.count()} products in database."
            )
        )
