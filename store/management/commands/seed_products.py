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
    ("Art", "Original paintings, illustrations, and prints made by hand."),
    ("Digital Art", "Illustrations, designs, and artwork created and delivered digitally."),
    ("3D Prints", "Designed and 3D-printed objects, models, and decor."),
]

# (shop_username, shop_name, shop_description, shop_location)
SHOPS = [
    ("claystudio", "The Clay Studio", "Handthrown stoneware inspired by the natural landscape.", "Bristol, UK"),
    ("woodlandcraft", "Woodland Craft Co.", "Sustainably sourced woodwork made in a forest workshop.", "Dorset, UK"),
    ("theweave", "The Weave", "Natural fibre textiles: linen, cotton, and wool.", "Edinburgh, UK"),
    ("amberforge", "Amber Forge", "Contemporary silver and gold jewellery with gemstone accents.", "London, UK"),
    ("sewnleather", "Sewn & Leather", "Vegetable-tanned leather goods built to last a lifetime.", "York, UK"),
    ("inkandcanvas", "Ink & Canvas Studio", "Original paintings and ink studies made in a small studio.", "Brighton, UK"),
    ("pixelfolk", "Pixelfolk Designs", "Custom digital illustration and character art delivered as print files.", "Manchester, UK"),
    ("layerworks", "Layerworks 3D", "Designed and 3D-printed models, figurines, and decor.", "Leeds, UK"),
]

# (shop_username, title, category_name, price, stock, featured, image_url, description, materials, made_to_order)
PRODUCTS = [
    (
        "claystudio", "Handthrown Stoneware Mug", "Ceramics", "28.00", 12, True,
        "assets/products/handthrown-stoneware-mug.jpg",
        "A beautifully weighted everyday mug with a comfortable handle and subtle glaze variations.",
        "Stoneware clay, food-safe glaze", False,
    ),
    (
        "claystudio", "Speckled Cereal Bowl", "Ceramics", "32.00", 8, False,
        "assets/products/speckled-cereal-bowl.jpg",
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
        "assets/products/turned-oak-salad-bowl.jpg",
        "Lathe-turned from a single piece of English oak, finished with food-safe oil.",
        "English oak, linseed oil", False,
    ),
    (
        "woodlandcraft", "Walnut Cheese Board", "Woodwork", "45.00", 7, False,
        "assets/products/walnut-cheese-board.jpg",
        "Hand-planed walnut serving board with a built-in juice groove.",
        "Black walnut, beeswax finish", False,
    ),
    (
        "woodlandcraft", "Carved Butter Spreader", "Woodwork", "14.00", 20, False,
        "assets/products/carved-butter-spreader.jpg",
        "Slim, ergonomic spreader carved by hand from cherry wood.",
        "Cherry wood", False,
    ),
    (
        "theweave", "Natural Linen Table Runner", "Textiles", "38.00", 6, True,
        "assets/products/natural-linen-table-runner.jpg",
        "Undyed linen runner woven on a floor loom. Softens beautifully with every wash.",
        "100% linen", False,
    ),
    (
        "theweave", "Merino Wool Throw", "Textiles", "120.00", 3, True,
        "assets/products/merino-wool-throw.jpg",
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
        "assets/products/sterling-silver-stacking-ring.jpg",
        "Slim band hand-formed and hammered for a subtle organic texture.",
        "Sterling silver (.925)", False,
    ),
    (
        "amberforge", "Moonstone Drop Earrings", "Jewellery", "72.00", 6, True,
        "assets/products/moonstone-drop-earrings.jpg",
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
        "assets/products/slim-bifold-wallet.jpg",
        "Four card slots and a cash pocket, saddle-stitched for decades of use.",
        "Vegetable-tanned cow leather, linen thread", False,
    ),
    (
        "sewnleather", "Waxed Canvas Tote", "Leather Goods", "95.00", 5, False,
        "assets/products/waxed-canvas-tote.jpg",
        "Heavy-duty tote with leather-reinforced handles and a magnetic snap closure.",
        "Waxed canvas, vegetable-tanned leather", False,
    ),
    (
        "sewnleather", "Personalised Luggage Tag", "Leather Goods", "22.00", 25, False,
        "assets/products/personalised-luggage-tag.jpg",
        "Debossed with your initials (up to 3 characters) — a classic travel gift.",
        "Vegetable-tanned leather", True,
    ),
    (
        "inkandcanvas", "Abstract Sunset Canvas", "Art", "150.00", 1, True,
        "assets/products/abstract-sunset-canvas.jpg",
        "Original acrylic painting in warm, layered tones — one-of-a-kind, signed on the back.",
        "Acrylic on canvas", False,
    ),
    (
        "inkandcanvas", "Monochrome Ink Study", "Art", "85.00", 1, False,
        "assets/products/monochrome-ink-study.jpg",
        "Loose, gestural ink study on heavyweight paper, framed and ready to hang.",
        "Ink on paper", False,
    ),
    (
        "inkandcanvas", "Citrus Bloom Original", "Art", "110.00", 0, False,
        "",
        "Custom floral still-life painted to your chosen colour palette.",
        "Acrylic on canvas", True,
    ),
    (
        "pixelfolk", "Whimsical Bird Swing Print", "Digital Art", "18.00", 50, True,
        "assets/products/whimsical-bird-swing-print.jpg",
        "High-resolution digital print delivered by download — a playful character illustration.",
        "Digital file (PNG/PDF)", False,
    ),
    (
        "pixelfolk", "Custom Cartoon Portrait", "Digital Art", "35.00", 0, False,
        "",
        "Send a photo and get a stylised cartoon portrait of yourself, a friend, or a pet.",
        "Digital file (PNG/PDF)", True,
    ),
    (
        "pixelfolk", "Character Concept Art Print", "Digital Art", "22.00", 40, False,
        "assets/products/character-concept-art-print.jpg",
        "Detailed character concept art, printable at home or framed.",
        "Digital file (PNG/PDF)", False,
    ),
    (
        "layerworks", "Articulated Dragon Figurine", "3D Prints", "32.00", 9, True,
        "assets/products/articulated-dragon-figurine.jpg",
        "Fully articulated dragon model, printed in PLA with moving joints — no assembly required.",
        "PLA plastic", False,
    ),
    (
        "layerworks", "Anatomical Skull Model", "3D Prints", "26.00", 11, False,
        "assets/products/anatomical-skull-model.jpg",
        "Detailed scale skull model, printed with fine layer resolution for crisp anatomical detail.",
        "PLA plastic", False,
    ),
    (
        "layerworks", "Geometric Petal Vase", "3D Prints", "29.00", 0, False,
        "assets/products/geometric-petal-vase.jpg",
        "Printed in a continuous spiral pattern — watertight liner included for fresh flowers.",
        "PLA plastic, glass liner", True,
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
            product, created = Product.objects.update_or_create(
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
            self.stdout.write(f"  {'Created' if created else 'Updated'} product: {title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {Category.objects.count()} categories, "
                f"{Shop.objects.count()} shops, "
                f"{Product.objects.count()} products in database."
            )
        )
