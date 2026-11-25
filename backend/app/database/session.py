"""Session helper for scripts and CLI commands (not for FastAPI routes).

FastAPI routes keep using the ``get_db`` dependency. Anything that runs
outside a request — seeders, ``manage.py`` commands — uses ``session_scope``
so commit / rollback / close always happen:

    with session_scope() as db:
        db.add(obj)
    # committed here; rolled back if an exception was raised
"""
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

from app.database.database import SessionLocal


@contextmanager
def session_scope() -> Iterator[Session]:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
