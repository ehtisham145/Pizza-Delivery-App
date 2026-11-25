<div align="center">

# 🍕 Pizza Delivery App

**A full-stack pizza ordering platform: FastAPI backend, React frontend, Docker + nginx deployment**

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[Features](#-features) · [Project Structure](#-project-structure) · [Local Development](#-local-development) · [Docker (Staging)](#-docker-staging) · [API Reference](#-api-reference)

</div>

---

## Overview

Customers browse the menu, fill a cart, save delivery addresses, place orders, pay and leave reviews. Admins and staff manage the menu, orders, users, payments and reviews from the same web app.

| Part | Tech | Folder |
|---|---|---|
| **Backend API** | FastAPI · SQLAlchemy 2 · Pydantic v2 · JWT (access + refresh) · bcrypt | [`backend/`](backend/) |
| **Frontend** | React 18 · Vite 5 · React Router 6 (no UI framework, plain CSS, light/dark) | [`frontend/`](frontend/) |
| **Reverse proxy** | nginx: `/api/*` → backend, everything else → frontend | [`nginx/`](nginx/) |
| **Deployment** | Docker Compose staging stack | [`docker/`](docker/) |

---

## ✨ Features

**Customers**
- Register / log in with JWT; the access token is refreshed automatically with the refresh token
- Browse pizzas by category, search, choose size (Small → X-large) and quantity
- Cart: add, change quantity, remove item, clear cart
- Up to 5 delivery addresses with a default one
- Place orders from the cart, view history, cancel pending orders
- Pay for an order (Card / Cash on Delivery) and view payment history
- Review delivered orders; read public reviews per pizza
- Notifications with unread badge, mark one / all as read
- Profile update and password change

**Admin / Staff**
- Dashboard: orders and revenue today and all-time, pending orders, user count *(admin)*
- Users: activate / deactivate, change role *(admin)*
- Orders: list and filter by status *(admin)*, open by ID and mark delivered / cancelled *(admin + staff)*
- Menu: create / edit pizzas, categories and toppings *(admin)*; toggle availability, delete pizzas, edit toppings *(admin + staff)*
- Payments: list all and update status *(admin)*
- Reviews: list and delete *(admin + staff)*

> **New accounts start inactive.** An admin must activate a user on **Admin → Users** before that user can log in.

---

## 📁 Project Structure

```
Pizza-Delivery-App/
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── database/
│   │   │   ├── database.py        # engine, SessionLocal, get_db (FastAPI dependency)
│   │   │   ├── session.py         # session_scope() for scripts / CLI
│   │   │   └── seeds/
│   │   │       ├── data.py        # seed data only (categories, sizes, toppings, pizzas, demo users)
│   │   │       └── seeders.py     # idempotent insert functions
│   │   ├── datamodels/            # SQLAlchemy models
│   │   ├── routes/                # API routers (auth, menu, cart, order, ...)
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   └── utils/                 # auth middleware, enums, validators, helpers
│   ├── requirements/
│   │   ├── base.txt               # shared runtime dependencies
│   │   ├── dev.txt                # base + pytest, ruff, pre-commit
│   │   └── prod.txt               # base + uvicorn[standard], PostgreSQL driver
│   ├── main.py                    # app entry point, router registration
│   ├── manage.py                  # database CLI: seed, create-admin, set-role, reset-db, ...
│   ├── pyproject.toml / uv.lock   # uv project files
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                      # React + Vite single-page app
│   ├── src/
│   │   ├── api/                   # client.js (fetch + token refresh), endpoints.js (every route)
│   │   ├── components/            # Layout, ProtectedRoute, shared UI
│   │   ├── context/               # AuthContext
│   │   ├── pages/                 # customer pages
│   │   │   └── admin/             # admin / staff pages
│   │   └── constants.js           # enums mirrored from the backend
│   ├── nginx.conf                 # serves the built SPA inside its container
│   ├── Dockerfile
│   └── .env.example
│
├── nginx/
│   └── nginx.conf                 # edge reverse proxy (/api → backend, / → frontend)
│
├── docker/
│   ├── docker-compose.staging.yaml
│   └── .env.staging.example
│
└── README.md
```

---

## 💻 Local Development

### Prerequisites
- Python **3.14** (see `backend/.python-version`) and [uv](https://github.com/astral-sh/uv) *or* pip
- Node.js **20+**

### 1. Backend

```bash
cd backend

# Option A: uv
uv venv
uv sync

# Option B: pip
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements/dev.txt

cp .env.example .env               # then set SECRET_KEY / REFRESH_SECRET_KEY
python main.py                     # runs on http://127.0.0.1:8002
```

Swagger docs: http://127.0.0.1:8002/docs

#### Database CLI (`manage.py`)

All database chores go through one CLI. Run it from `backend/` with the same `.env` as the API.

```bash
python manage.py seed                        # categories, sizes, toppings, pizzas
python manage.py create-admin you@example.com
```

| Command | What it does |
|---|---|
| `init-db` | Create any missing tables |
| `seed [--only a,b]` | Insert seed data. Safe to re-run: existing rows are skipped. Choices: `categories,sizes,toppings,pizzas,users` |
| `seed --only users` | 21 demo customers (password `Ehti@123`, inactive). **Dev only**, never run by default |
| `create-admin EMAIL` | Give a registered user the `admin` role and activate them |
| `set-role EMAIL ROLE` | `admin` / `staff` / `user` / `customer` |
| `activate-user EMAIL` / `deactivate-user EMAIL` | Allow / block login |
| `tables` | List tables with row counts |
| `clear-orders [--yes]` | ⚠️ Delete all carts, orders, payments and reviews |
| `reset-db [--yes] [--seed]` | ⚠️ Drop and recreate every table, optionally re-seed |

⚠️ commands ask you to type `yes` first (`--yes` skips the prompt) and **refuse to run when `APP_ENV=production`**.

Seed data lives in `app/database/seeds/data.py`; edit it there. Sizes are seeded in the order Small, Medium, Large, X-large, because the frontend expects size IDs 1–4 in that order (`frontend/src/constants.js`).

#### First-time setup

```bash
python manage.py seed
# register in the web app, then:
python manage.py create-admin you@example.com
```

### 2. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev                        # http://localhost:5173
```

Vite proxies `/api/*` to `VITE_DEV_API_TARGET` (default `http://127.0.0.1:8002`) and strips the `/api` prefix, exactly like nginx does in Docker, so no CORS setup is needed.

### Requirements files

| File | Use | Contents |
|---|---|---|
| `requirements/base.txt` | everywhere | FastAPI, SQLAlchemy, Pydantic, JWT, bcrypt, dotenv |
| `requirements/dev.txt` | local development | `base` + pytest, pytest-cov, httpx, ruff, pre-commit |
| `requirements/prod.txt` | Docker / servers | `base` + `uvicorn[standard]`, `psycopg2-binary` |

---

## 🐳 Docker (Staging)

The staging stack runs three containers:

```
           :80
  browser ─────▶ nginx ──/api/*──▶ backend  (FastAPI :8000, SQLite on a volume)
                   │
                   └──── /* ─────▶ frontend (static React build)
```

```bash
# from the repository root
cp docker/.env.staging.example docker/.env.staging     # fill in real secrets
docker compose -f docker/docker-compose.staging.yaml up -d --build
```

| URL | What |
|---|---|
| `http://<server>/` | Web app |
| `http://<server>/docs` | Swagger UI |
| `http://<server>/api/...` | API (prefix stripped by nginx) |

**Useful commands**

```bash
docker compose -f docker/docker-compose.staging.yaml ps
docker compose -f docker/docker-compose.staging.yaml logs -f backend
docker compose -f docker/docker-compose.staging.yaml down          # keeps the database volume
```

**Database commands inside the container**

```bash
docker compose -f docker/docker-compose.staging.yaml exec backend python manage.py seed
docker compose -f docker/docker-compose.staging.yaml exec backend python manage.py create-admin you@example.com
docker compose -f docker/docker-compose.staging.yaml exec backend python manage.py tables
```

**Port 80 already in use?** Another project on the server may own it. Publish on a different port:

```bash
PIZZA_HTTP_PORT=8081 docker compose -f docker/docker-compose.staging.yaml up -d
```

The stack uses its own Compose project name (`pizza-delivery-staging`), so it never replaces containers from other projects on the same server.

---

## 📡 API Reference

All paths below are backend paths. From the browser (and through nginx), prefix them with `/api`.
🔓 public · 👤 logged-in user · 🛠 admin or staff · 👑 admin

### Authentication: `/auth`
| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/auth/register` | 🔓 | Create an account (starts inactive) |
| POST | `/auth/login` | 🔓 | Form login (`username`=email, `password`) → access + refresh token |
| POST | `/auth/logout` | 👤 | Blacklist the current access token |
| POST | `/auth/refresh-token` | 🔓 | Swap a refresh token for a new token pair |

### Profile: `/profile`
| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/profile/get-user-profile` | 👤 | Current user |
| PUT | `/profile/update-profile` | 👤 | Update name and phone |
| PUT | `/profile/change-password` | 👤 | Change password |

### Menu: `/menu`
| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/menu/get_all_pizzas` | 👤 | All pizzas |
| GET | `/menu/pizza_by_id/{pizza_id}` | 👤 | One pizza |
| POST | `/menu/create_pizza` | 👑 | Create pizza |
| PUT | `/menu/update_pizza/{pizza_id}` | 👑 | Update pizza |
| PATCH | `/menu/update_pizza_status/{pizza_id}` | 🛠 | Toggle availability |
| DELETE | `/menu/pizzas/{pizza_id}` | 🛠 | Delete pizza |
| GET | `/menu/view_categories` | 👤 | All categories |
| POST | `/menu/create_category` | 👑 | Create category |
| GET | `/menu/all_toppings` | 👤 | All toppings |
| POST | `/menu/create_toppings` | 👑 | Create topping |
| PUT | `/menu/update_topping/{topping_id}` | 🛠 | Update topping |

### Cart: `/cart`
| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/cart/get_your_cart` | 👤 | Cart with items and total |
| POST | `/cart/add_item_to_cart/{item_id}` | 👤 | Add pizza (`size_id`, `quantity`) |
| PATCH | `/cart/update_cart_Item_quantity?item_id=&quantity=` | 👤 | Change quantity |
| DELETE | `/cart/delete_cart_item/{item_id}` | 👤 | Remove one item |
| DELETE | `/cart/delete_entire_cart` | 👤 | Clear cart |

### Delivery addresses: `/delivery`
| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/delivery/add_new_address/customer` | 👤 | Add address (max 5) |
| GET | `/delivery/get_all_addresses/customer` | 👤 | List addresses |
| PATCH | `/delivery/set_default_address/customer/{address_id}` | 👤 | Set default |
| PATCH | `/delivery/update_address/customer/{address_id}` | 👤 | Update address |
| DELETE | `/delivery/delete_Address/customer/{address_id}` | 👤 | Delete address |

### Orders: `/order`
| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/order/place_order_from_cart/user` | 👤 | Place order from cart |
| GET | `/order/get_orders_history/user` | 👤 | My order history |
| GET | `/order/get_order_by_id/user/{order_id}` | 👤 | One of my orders |
| PATCH | `/order/cancel_Order/User/{order_id}` | 👤 | Cancel a pending order |
| GET | `/order/get_all_orders/admin?page=&page_size=&order_status=` | 👑 | All orders, paginated |
| GET | `/order/admin/get_orders/{order_id}` | 🛠 | Any order by ID |
| PATCH | `/order/update_order_status/admin/{order_id}` | 🛠 | Set status |

### Payments: `/payment`
| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/payment/create_payment` | 👤 | Pay for an order |
| GET | `/payment/get_payment_history/customer` | 👤 | My payments |
| GET | `/payment/get_payment_detail/customer/{order_id}` | 👤 | Payment for one order |
| GET | `/payment/get_all_payments/admin` | 👑 | All payments |
| PATCH | `/payment/update_payment_status/admin/{payment_id}` | 👑 | Update status |

### Reviews: `/review`
| Method | Path | Access | Description |
|---|---|---|---|
| POST | `/review/submit_review` | 👤 | Review an order |
| GET | `/review/history` | 👤 | My reviews |
| GET | `/review/reviews/pizza/{pizza_id}` | 🔓 | Reviews for a pizza |
| GET | `/review/reviews` | 👑 | All reviews |
| DELETE | `/review/reviews/{review_id}` | 🛠 | Delete review |

### Notifications: `/notifications`
| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/notifications/get_notifications?page=&size=` | 👤 | Paginated notifications |
| PATCH | `/notifications/mark_as_read_notification/{notification_id}` | 👤 | Mark one read |
| PATCH | `/notifications/mark_all_notification_as_read` | 👤 | Mark all read |
| GET | `/notifications/unread/notifications/count` | 👤 | Unread count |

### Admin: `/admin`
| Method | Path | Access | Description |
|---|---|---|---|
| GET | `/admin/get_stats_admin` | 👑 | Dashboard stats |
| GET | `/admin/get_all_user/admin` | 👑 | All users |
| PATCH | `/admin/activate_user/admin/{user_id}` | 👑 | Activate user |
| PATCH | `/admin/deactivate_user/admin/{user_id}` | 👑 | Deactivate user |
| PATCH | `/admin/change_role/admin/{user_id}?assign_role=` | 👑 | Change role (`user` / `staff` / `admin`) |
| GET | `/admin/get_all_orders/admin/{order_status}` | 👑 | Orders by status |

---

## 🔐 Environment Variables

| Variable | Where | Example |
|---|---|---|
| `DATABASE_URL` | backend | `sqlite:///./pizza_delivery.db` |
| `SECRET_KEY` | backend | long random string |
| `REFRESH_SECRET_KEY` | backend | a different long random string |
| `ALGORITHM` | backend | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | backend | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | backend | `7` |
| `VITE_API_BASE_URL` | frontend (build time) | `/api` |
| `VITE_DEV_API_TARGET` | frontend (dev only) | `http://127.0.0.1:8002` |
| `PIZZA_HTTP_PORT` | docker compose | `80` |

Never commit real `.env` files; only the `*.example` files belong in git.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

<div align="center">

Made with ❤️ by **[Ehtisham](https://github.com/ehtisham145)**

</div>
