import logging
from app.database.database import engine, Base
logger = logging.getLogger(__name__)


def create_tables():
    """Create any missing tables. Existing tables and their data are left untouched.

    Called once from main.py on startup — importing this module does nothing by itself.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables are ready.")
