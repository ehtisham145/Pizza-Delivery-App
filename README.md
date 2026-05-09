<div align="center">

# 🍕 Pizza Delivery API

**A production-ready REST API for a complete Pizza Delivery platform**  
Built with FastAPI · SQLAlchemy · JWT Authentication · Role-Based Access Control

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://sqlalchemy.org)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[Features](#-features) · [Tech Stack](#-tech-stack) · [Getting Started](#-getting-started) · [API Reference](#-api-reference) · [Project Structure](#-project-structure)

</div>

---

## 📌 Overview

Pizza Delivery API is a fully-featured backend system for managing an end-to-end pizza delivery service. It covers everything from secure user authentication to order management, payments, reviews, and real-time notifications — all designed with clean architecture and production best practices.

---

## ✨ Features

### 🔐 Authentication & Security
- **JWT Dual-Token System** — Short-lived Access Tokens + long-lived Refresh Tokens
- **BCrypt Password Hashing** — Secure password storage via Passlib
- **OAuth2 Password Flow** — Industry-standard authentication
- **RBAC** — Role-Based Access Control (Admin vs Customer)
- **IDOR Protection** — All resources validated against the authenticated user

### 👤 User Management
- Secure registration & login
- Profile update (username, email, phone)
- Password change with current password verification
- Token refresh without re-login

### 🍕 Pizza Catalog
- Browse available pizzas with details & pricing
- Admin: add, update, and remove pizzas
- Category and availability management

### 📦 Order Management
- Place orders with multiple pizzas
- Real-time order status tracking
- Order history with pagination
- Admin: view and update all orders

### 💳 Payment System
- Create payment linked to an order
- Race-condition-safe duplicate payment prevention
- Admin: update payment status
- Full payment history per user

### ⭐ Reviews
- Submit one review per delivered order
- Public pizza reviews (by pizza ID)
- Admin: moderate and delete reviews
- Ownership-enforced review access

### 🔔 Notifications
- Real-time notification delivery per user
- Mark single or all notifications as read
- Unread count badge support
- Paginated notification history

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | FastAPI |
| **ORM** | SQLAlchemy 2.0 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Auth** | JWT (PyJWT) + Passlib (BCrypt) |
| **Validation** | Pydantic V2 |
| **Package Manager** | uv |
| **Server** | Uvicorn |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### 1. Clone the repository
```bash
git clone https://github.com/ehtisham145/Pizza-Delivery-App.git
cd Pizza-Delivery-App
```

### 2. Create and activate virtual environment
```bash
uv venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
uv sync
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=sqlite:///./pizza_delivery.db
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

### 5. Start the development server
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`  
Interactive docs at `http://127.0.0.1:8000/docs`

---

## 📡 API Reference

### 🔐 Auth Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/auth/signup` | Register a new user | Public |
| `POST` | `/auth/login` | Login and get tokens | Public |
| `POST` | `/auth/refresh` | Refresh access token | Public |

### 👤 User Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/user/me` | Get current user profile | Customer |
| `PUT` | `/user/update` | Update username / email | Customer |
| `PATCH` | `/user/password` | Change password | Customer |
| `PATCH` | `/user/phone` | Update phone number | Customer |

### 🍕 Pizza Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/pizzas/` | List all available pizzas | Public |
| `GET` | `/pizzas/{pizza_id}` | Get pizza details | Public |
| `POST` | `/pizzas/` | Add a new pizza | Admin |
| `PATCH` | `/pizzas/{pizza_id}` | Update pizza info | Admin |
| `DELETE` | `/pizzas/{pizza_id}` | Remove a pizza | Admin |

### 📦 Order Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/orders/` | Place a new order | Customer |
| `GET` | `/orders/history` | Get order history | Customer |
| `GET` | `/orders/{order_id}` | Get order detail | Customer |
| `GET` | `/orders/admin/all` | Get all orders | Admin |
| `PATCH` | `/orders/{order_id}/status` | Update order status | Admin |

### 💳 Payment Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/payments/` | Create a payment | Customer |
| `GET` | `/payments/history` | Get payment history | Customer |
| `GET` | `/payments/order/{order_id}` | Get payment for an order | Customer |
| `GET` | `/payments/admin/all` | Get all payments | Admin |
| `PATCH` | `/payments/{payment_id}/status` | Update payment status | Admin |

### ⭐ Review Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/reviews/` | Submit a review | Customer |
| `GET` | `/reviews/history` | Get my reviews | Customer |
| `GET` | `/reviews/pizza/{pizza_id}` | Get reviews for a pizza | Public |
| `GET` | `/reviews/admin/all` | Get all reviews | Admin |
| `DELETE` | `/reviews/{review_id}` | Delete a review | Admin |

### 🔔 Notification Endpoints

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/notifications/` | Get notifications | Customer |
| `GET` | `/notifications/unread/count` | Get unread count | Customer |
| `PATCH` | `/notifications/{id}/read` | Mark one as read | Customer |
| `PATCH` | `/notifications/read-all` | Mark all as read | Customer |

---

## 🗂 Project Structure

```
Pizza-Delivery-App/
│
├── App/
│   ├── Database/
│   │   └── database.py          # DB engine & session management
│   │
│   ├── DataModels/              # SQLAlchemy ORM models
│   │   ├── Auth_Users/
│   │   ├── Order/
│   │   ├── Payment/
│   │   ├── Reviews/
│   │   └── Notifications/
│   │
│   ├── Schemas/                 # Pydantic request/response schemas
│   │   ├── Auth_Users/
│   │   ├── Order/
│   │   ├── Payment/
│   │   ├── Reviews/
│   │   └── Notifications/
│   │
│   ├── Routes/                  # API route handlers
│   │   ├── auth_routes.py
│   │   ├── user_routes.py
│   │   ├── pizza_routes.py
│   │   ├── order_routes.py
│   │   ├── payment_routes.py
│   │   ├── review_routes.py
│   │   └── notification_routes.py
│   │
│   └── Utils/
│       ├── middleware.py        # Auth guards (get_current_user, require_admin)
│       └── constant.py          # Enums & constants
│
├── main.py                      # FastAPI app entry point
├── pyproject.toml               # Project dependencies
├── uv.lock                      # Locked dependency versions
├── .env                         # Environment variables (not committed)
├── .gitignore
└── README.md
```

---

## 🔒 Security Design

- All protected routes require a valid `Bearer` token in the `Authorization` header
- Ownership is verified at the database level — users can only access their own resources
- Admin routes are protected by a separate `require_admin` dependency
- Duplicate resource creation is handled via `IntegrityError` to prevent race conditions
- Passwords are never stored or returned in plain text

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ by **[Ehtisham](https://github.com/ehtisham145)**

⭐ Star this repo if you found it useful!

</div>