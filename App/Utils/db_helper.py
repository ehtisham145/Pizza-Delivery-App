from sqlalchemy.orm import Session


def safe_commit(db: Session) -> None:
    """
    Rollback + re-raise on failure.
    """
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise 