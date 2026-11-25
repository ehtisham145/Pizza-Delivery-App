"""Database management CLI.

Run from the backend/ folder (needs the same .env as the API):

    python manage.py --help
    python manage.py init-db
    python manage.py seed                         # categories, sizes, toppings, pizzas
    python manage.py seed --only sizes,pizzas
    python manage.py seed --only users            # demo users (dev only)
    python manage.py create-admin you@example.com
    python manage.py set-role someone@example.com staff
    python manage.py activate-user someone@example.com
    python manage.py deactivate-user someone@example.com
    python manage.py tables
    python manage.py clear-orders                 # destructive, asks first
    python manage.py reset-db --seed              # destructive, asks first

Destructive commands ask for confirmation (skip with --yes) and refuse to
run at all when APP_ENV=production.
"""
import argparse
import os
import sys

from sqlalchemy import func, inspect

from app.database.database import Base, engine
from app.database.session import session_scope

ROLES = ["admin", "staff", "user", "customer"]


# ── Helpers ─────────────────────────────────────────────────────
def load_models() -> None:
    """Import every model so Base.metadata knows all tables."""
    import app.datamodels.Auth_Users.black_list_token_model  # noqa: F401
    import app.datamodels.Auth_Users.refresh_token_model  # noqa: F401
    import app.datamodels.Auth_Users.user_model  # noqa: F401
    import app.datamodels.Cart.cart_model  # noqa: F401
    import app.datamodels.Delivery.delivery_model  # noqa: F401
    import app.datamodels.Menu.menu_model  # noqa: F401
    import app.datamodels.Notifications.notification_model  # noqa: F401
    import app.datamodels.Order.order_model  # noqa: F401
    import app.datamodels.Payment.payment_model  # noqa: F401
    import app.datamodels.Reviews.reviews_model  # noqa: F401


def fail(message: str) -> None:
    print(f"[error] {message}", file=sys.stderr)
    sys.exit(1)


def guard_destructive(args: argparse.Namespace, what: str) -> None:
    if os.getenv("APP_ENV", "").lower() == "production":
        fail(f"Refusing to {what}: APP_ENV=production.")
    if args.yes:
        return
    answer = input(f"[warning] This will {what}. Type 'yes' to continue: ").strip().lower()
    if answer != "yes":
        fail("Aborted.")


def get_user(db, email: str):
    from app.datamodels.Auth_Users.user_model import User

    user = db.query(User).filter(func.lower(User.email) == email.strip().lower()).first()
    if not user:
        fail(f"No user with email {email}.")
    return user


# ── Commands ────────────────────────────────────────────────────
def cmd_init_db(args):
    Base.metadata.create_all(bind=engine)
    print("[ok] Tables created (existing tables were left untouched).")


def cmd_seed(args):
    from app.database.seeds import DEFAULT_SEEDERS, SEEDERS, run_seeders

    names = [n.strip() for n in args.only.split(",") if n.strip()] if args.only else DEFAULT_SEEDERS
    Base.metadata.create_all(bind=engine)
    try:
        with session_scope() as db:
            results = run_seeders(db, names)
    except (ValueError, RuntimeError) as exc:
        fail(str(exc))

    for name in SEEDERS:
        if name in results:
            inserted, skipped = results[name]
            print(f"[ok] {name:<11} inserted {inserted:>3}, already existed {skipped:>3}")


def cmd_create_admin(args):
    with session_scope() as db:
        user = get_user(db, args.email)
        user.role = "admin"
        user.is_active = True
        print(f"[ok] {user.email} is now an active admin.")


def cmd_set_role(args):
    with session_scope() as db:
        user = get_user(db, args.email)
        old = user.role
        user.role = args.role
        print(f"[ok] {user.email}: {old} -> {args.role}")


def cmd_set_active(active: bool):
    def run(args):
        with session_scope() as db:
            user = get_user(db, args.email)
            user.is_active = active
            print(f"[ok] {user.email} is now {'active' if active else 'inactive'}.")

    return run


def cmd_tables(args):
    names = inspect(engine).get_table_names()
    if not names:
        print("No tables yet. Run: python manage.py init-db")
        return
    from sqlalchemy import text

    with engine.connect() as conn:
        for name in sorted(names):
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar()
            print(f"{name:<24} {count:>6} rows")


def cmd_clear_orders(args):
    guard_destructive(args, "delete ALL carts, orders, payments and reviews")
    from app.datamodels.Cart.cart_model import Cart_Item, Cart_Item_Topping, Cart_Model
    from app.datamodels.Order.order_model import Order_Item_Model, Order_Model, Order_Topping_Model
    from app.datamodels.Payment.payment_model import Payment_Model
    from app.datamodels.Reviews.reviews_model import Review_Model

    # Children before parents so foreign keys are never left dangling.
    order = [
        Review_Model, Payment_Model, Order_Topping_Model, Order_Item_Model, Order_Model,
        Cart_Item_Topping, Cart_Item, Cart_Model,
    ]
    with session_scope() as db:
        for model in order:
            deleted = db.query(model).delete(synchronize_session=False)
            print(f"  deleted {model.__tablename__:<20} {deleted:>6} rows")
    print("[ok] Order data cleared.")


def cmd_reset_db(args):
    guard_destructive(args, "DROP every table and recreate an empty database")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[ok] Database reset.")
    if args.seed:
        args.only = None
        cmd_seed(args)


# ── CLI wiring ──────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="manage.py", description="Pizza Delivery database management")
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    sub.add_parser("init-db", help="create any missing tables").set_defaults(func=cmd_init_db)

    p = sub.add_parser("seed", help="insert seed data (safe to run repeatedly)")
    p.add_argument("--only", help="comma-separated: categories,sizes,toppings,pizzas,users")
    p.set_defaults(func=cmd_seed)

    p = sub.add_parser("create-admin", help="make a registered user an active admin")
    p.add_argument("email")
    p.set_defaults(func=cmd_create_admin)

    p = sub.add_parser("set-role", help="change a user's role")
    p.add_argument("email")
    p.add_argument("role", choices=ROLES)
    p.set_defaults(func=cmd_set_role)

    p = sub.add_parser("activate-user", help="allow a user to log in")
    p.add_argument("email")
    p.set_defaults(func=cmd_set_active(True))

    p = sub.add_parser("deactivate-user", help="block a user from logging in")
    p.add_argument("email")
    p.set_defaults(func=cmd_set_active(False))

    sub.add_parser("tables", help="list tables with row counts").set_defaults(func=cmd_tables)

    p = sub.add_parser("clear-orders", help="DELETE all carts, orders, payments, reviews")
    p.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    p.set_defaults(func=cmd_clear_orders)

    p = sub.add_parser("reset-db", help="DROP and recreate every table")
    p.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    p.add_argument("--seed", action="store_true", help="run the default seeders afterwards")
    p.set_defaults(func=cmd_reset_db)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    load_models()
    args.func(args)


if __name__ == "__main__":
    main()
