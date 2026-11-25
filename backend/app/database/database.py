import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

# ----------------- Base -------------------
# The declarative_base class is used to map Python classes to database tables.
# It serves as a base class for all your database models.
Base = declarative_base()

# ----------------- DB URL ------------------------------
# Read from the DATABASE_URL environment variable (set in .env / docker compose).
# Falls back to a local SQLite file in the current directory for development.
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./pizza_delivery.db")

# ------------------ Create Connection ------------------
# We use create_engine to establish a connection between the Python application and the database.
# 'check_same_thread': False is specifically required for SQLite when used with FastAPI.
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, connect_args=connect_args)

# ------------------ Create Session Factory ---------------------
# sessionmaker is used to define the properties of the database session.
# It acts as a factory that generates session objects whenever a connection is needed.
# These sessions are used to perform CRUD (Create, Read, Update, Delete) operations.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------ Dependency ------------------------
# This generator function creates a database session for each request.
# The 'yield' keyword provides the session to the FastAPI route.
# The 'finally' block ensures that the session is always closed after the request is finished,
# preventing memory leaks or database connection hanging.
def get_db():
    db: Session = SessionLocal()
    try:
        yield db  
    finally:
        db.close()
