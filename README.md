### 🍕 Pizza Delivery API: Authorization Module

A secure, production-ready FastAPI backend module focused on robust Authentication and Authorization workflows. This module serves as the security backbone for the Pizza Delivery system, ensuring data integrity and secure user access.
🔐 Core Features

## 1. Advanced Authentication

    User Registration: Secure signup flow featuring automated password hashing via BCrypt.

    OAuth2 Implementation: Utilizes the OAuth2 Password Grant flow for standardized security.

    JWT Dual-Token System:

        Access Tokens: Short-lived tokens to minimize the window of vulnerability.

        Refresh Tokens: Long-lived tokens allowing users to maintain sessions without re-authenticating frequently.

## 2. Identity & Access Management

    RBAC (Role-Based Access Control): Integrated logic to restrict access to specific resources based on user roles (e.g., Admin vs. Customer).

    Profile Security: Dedicated endpoints for managing sensitive user data, including protected updates for passwords and contact information.

## 3. Validation & Performance

    Pydantic V2: Leverages the latest Pydantic version for high-speed data validation and strict type safety.

    Async Persistence: Optimized database interactions using SQLAlchemy for non-blocking I/O.

🛠️ Tech Stack

Component	Technology
Framework	FastAPI
Database	PostgreSQL + SQLAlchemy
Security	JWT (PyJWT), Passlib (BCrypt)
Validation	Pydantic V2

##📂 Project Structure

The project follows a modular architecture to ensure separation of concerns and maintainability:
Plaintext

├── App/
│   ├── Database/    # Database engine, session management, and migrations
│   ├── Models/      # SQLAlchemy ORM definitions (User, Token models)
│   ├── Schemas/     # Pydantic models for request/response validation
│   ├── Routes/      # API controllers (Auth and User logic)
│   └── Security/    # JWT generation, token rotation, and hashing utilities
├── main.py          # FastApi application entry point
└── .env             # Environment variables and secret keys

📍 API Reference

Authentication Endpoints
Method	Endpoint	Description
POST	/auth/signup	Register a new user account
POST	/auth/login	Authenticate user and receive Access/Refresh tokens
POST	/auth/refresh	Obtain a new Access Token using a valid Refresh Token
User Management (Protected)
Method	Endpoint	Description
GET	/user/me	Retrieve the currently logged-in user's profile
PUT	/user/update	Update general profile info (Username/Email)
PATCH	/user/password	Securely update account password
PATCH	/user/phone	Update verified phone number


🚀 Getting Started
1. Environment Setup
Bash

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install core dependencies
pip install fastapi uvicorn sqlalchemy psycopg2 passlib[bcrypt] python-jose[cryptography]

2. Configuration

Create a .env file in the root directory and define your secrets:
Code snippet

DATABASE_URL=postgresql://user:password@localhost/pizza_db
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

3. Launch
Bash

# Initialize database tables
python -m App.Database.init_db

# Start the development server
uvicorn main:app --reload
