"""Seeder functions. Each one is idempotent: rows that already exist are
skipped, so running ``python manage.py seed`` twice never creates duplicates.

Every seeder takes an open session and returns ``(inserted, skipped)``.
The caller (``run_seeders``) owns the transaction.
"""
from typing import Callable

from sqlalchemy.orm import Session

from app.database.seeds import data
from app.datamodels.Auth_Users.user_model import User
from app.datamodels.Menu.menu_model import Category_Model, Pizza_Model, Size_Model, Topping_Model

SeedResult = tuple[int, int]


def seed_categories(db: Session) -> SeedResult:
    inserted = skipped = 0
    for item in data.CATEGORIES:
        if db.query(Category_Model).filter(Category_Model.name == item["name"]).first():
            skipped += 1
            continue
        db.add(Category_Model(name=item["name"], description=item["description"]))
        inserted += 1
    return inserted, skipped


def seed_sizes(db: Session) -> SeedResult:
    inserted = skipped = 0
    for item in data.SIZES:
        if db.query(Size_Model).filter(Size_Model.size == item["size"]).first():
            skipped += 1
            continue
        db.add(Size_Model(size=item["size"], price_multiplier=item["price_multiplier"]))
        db.flush()  # keep insertion order -> predictable IDs (1..4) on a fresh DB
        inserted += 1
    return inserted, skipped


def seed_toppings(db: Session) -> SeedResult:
    inserted = skipped = 0
    for item in data.TOPPINGS:
        if db.query(Topping_Model).filter(Topping_Model.name == item["name"]).first():
            skipped += 1
            continue
        db.add(Topping_Model(**item))
        inserted += 1
    return inserted, skipped


def seed_pizzas(db: Session) -> SeedResult:
    categories = {c.name: c.id for c in db.query(Category_Model).all()}
    missing = {p["category"] for p in data.PIZZAS} - set(categories)
    if missing:
        names = ", ".join(sorted(m.value for m in missing))
        raise RuntimeError(f"Missing categories: {names}. Seed categories first.")

    inserted = skipped = 0
    for item in data.PIZZAS:
        if db.query(Pizza_Model).filter(Pizza_Model.name == item["name"]).first():
            skipped += 1
            continue
        db.add(
            Pizza_Model(
                name=item["name"],
                description=item["description"],
                base_price=item["base_price"],
                category_id=categories[item["category"]],
                image_url=data.pizza_image_url(item["name"]),
                is_available=True,
            )
        )
        inserted += 1
    return inserted, skipped


def seed_demo_users(db: Session) -> SeedResult:
    # Imported lazily: middleware needs SECRET_KEY etc. from the environment.
    from app.utils.middleware import get_password_hash

    password_hash = get_password_hash(data.DEMO_USER_PASSWORD)
    inserted = skipped = 0
    for item in data.demo_users():
        if db.query(User).filter(User.email == item["email"]).first():
            skipped += 1
            continue
        db.add(User(**item, password=password_hash))
        inserted += 1
    return inserted, skipped


# Order matters: pizzas need categories.
SEEDERS: dict[str, Callable[[Session], SeedResult]] = {
    "categories": seed_categories,
    "sizes": seed_sizes,
    "toppings": seed_toppings,
    "pizzas": seed_pizzas,
    "users": seed_demo_users,
}

# What `manage.py seed` runs without --only. Demo users are opt-in.
DEFAULT_SEEDERS = ["categories", "sizes", "toppings", "pizzas"]


def run_seeders(db: Session, names: list[str]) -> dict[str, SeedResult]:
    unknown = [n for n in names if n not in SEEDERS]
    if unknown:
        raise ValueError(f"Unknown seeder(s): {', '.join(unknown)}. Choose from: {', '.join(SEEDERS)}")

    results = {}
    for name in SEEDERS:  # always run in dependency order
        if name in names:
            results[name] = SEEDERS[name](db)
            db.flush()
    return results
