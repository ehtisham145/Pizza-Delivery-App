"""Seed data only — no database code lives here.

Edit these lists to change what ``python manage.py seed`` inserts.
"""
from decimal import Decimal

from app.utils.constant import PizzaCategoryEnum, PizzaSizeEnum, PizzaToppingEnum

# ── Categories ──────────────────────────────────────────────────
CATEGORIES: list[dict] = [
    {"name": PizzaCategoryEnum.SIGNATURE, "description": "Our timeless recipes featuring traditional flavors and high-quality ingredients."},
    {"name": PizzaCategoryEnum.MEAT_FEAST, "description": "A protein-packed delight loaded with premium pepperoni, succulent beef, and smoky chicken."},
    {"name": PizzaCategoryEnum.GARDEN_FRESH, "description": "A vibrant selection of garden-fresh vegetables and aromatic herbs."},
    {"name": PizzaCategoryEnum.CHEESY, "description": "The ultimate treat for cheese lovers, featuring a rich blend of melted cheeses."},
    {"name": PizzaCategoryEnum.SPICY, "description": "Turn up the heat with our selection of spicy jalapeños and zesty sauces."},
    {"name": PizzaCategoryEnum.FUSION, "description": "An adventurous mix of unique global flavors and gourmet toppings."},
]

# ── Sizes ───────────────────────────────────────────────────────
# Keep this order: the frontend (frontend/src/constants.js) expects
# IDs 1–4 to be Small, Medium, Large, X-large on a fresh database.
SIZES: list[dict] = [
    {"size": PizzaSizeEnum.SMALL, "price_multiplier": Decimal("1.0")},
    {"size": PizzaSizeEnum.MEDIUM, "price_multiplier": Decimal("1.5")},
    {"size": PizzaSizeEnum.LARGE, "price_multiplier": Decimal("2.0")},
    {"size": PizzaSizeEnum.EXTRA_LARGE, "price_multiplier": Decimal("2.5")},
]

# ── Toppings ────────────────────────────────────────────────────
DEFAULT_TOPPING_PRICE = Decimal("150.00")
TOPPINGS: list[dict] = [
    {"name": topping.value, "extra_price": DEFAULT_TOPPING_PRICE, "is_available": True}
    for topping in PizzaToppingEnum
]

# ── Pizzas ──────────────────────────────────────────────────────
# `category` is resolved to an ID at seed time, so categories must be seeded first.
PIZZAS: list[dict] = [
    {"name": "Chicken Tikka", "base_price": Decimal("1200"), "category": PizzaCategoryEnum.SIGNATURE, "description": "Traditional tikka chunks with onions."},
    {"name": "Pepperoni Passion", "base_price": Decimal("1450"), "category": PizzaCategoryEnum.MEAT_FEAST, "description": "Extra pepperoni with double mozzarella."},
    {"name": "Veggie Supreme", "base_price": Decimal("1100"), "category": PizzaCategoryEnum.GARDEN_FRESH, "description": "Bell peppers, olives, mushrooms, and onions."},
    {"name": "Fiery Jalapeno", "base_price": Decimal("1300"), "category": PizzaCategoryEnum.SPICY, "description": "Spicy chicken with a heavy dose of jalapenos."},
    {"name": "Beef Delight", "base_price": Decimal("1600"), "category": PizzaCategoryEnum.MEAT_FEAST, "description": "Premium ground beef with smoky BBQ sauce."},
    {"name": "Fajita Sensation", "base_price": Decimal("1250"), "category": PizzaCategoryEnum.SIGNATURE, "description": "Marinated fajita chicken and green peppers."},
    {"name": "Mushroom Magic", "base_price": Decimal("1150"), "category": PizzaCategoryEnum.GARDEN_FRESH, "description": "Freshly sliced mushrooms and creamy white sauce."},
    {"name": "Peri Peri Blast", "base_price": Decimal("1400"), "category": PizzaCategoryEnum.SPICY, "description": "Hot peri-peri chicken with spicy red chilies."},
    {"name": "Cheese Lover", "base_price": Decimal("1000"), "category": PizzaCategoryEnum.SIGNATURE, "description": "A rich blend of cheddar, mozzarella, and parmesan."},
    {"name": "BBQ Chicken", "base_price": Decimal("1350"), "category": PizzaCategoryEnum.MEAT_FEAST, "description": "Grilled chicken tossed in sweet and tangy BBQ sauce."},
]


def pizza_image_url(name: str) -> str:
    return f"uploads/pizzas/{name.lower().replace(' ', '_')}.jpg"


# ── Demo users (development only) ───────────────────────────────
# Inserted only with `python manage.py seed --only users`; never by default.
DEMO_USER_PASSWORD = "Ehti@123"
DEMO_USER_NAMES: list[str] = [
    "Ehtisham", "Ahmed Ali", "Fatima Khan", "Zubair Sheikh", "Sana Malik", "Usman Ghani",
    "Ayesha Siddiqa", "Hamza Yusuf", "Bilal Ahmed", "Zainab Bibi", "Omer Farooq",
    "Maryam Nawaz", "Mustafa Kamal", "Hina Rabbani", "Asad Umar", "Faisal Javed",
    "Khadija Tul", "Imran Khan", "Babar Azam", "Rizwan Ahmed", "Shaheen Afridi",
]


def demo_users() -> list[dict]:
    users = []
    for i, name in enumerate(DEMO_USER_NAMES):
        users.append(
            {
                "full_name": name,
                "email": f"{name.replace(' ', '').lower()}exp@gmail.com",
                "phone_number": f"0300{1000000 + i}",
                "role": "customer",
                "is_active": False,
            }
        )
    return users
