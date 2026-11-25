from sqlalchemy.orm import Session

from app.datamodels.Notifications.notification_model import Notification_Model


def create_notification(db: Session, user_id: int, title: str, message: str) -> Notification_Model:
    """Queue a notification for a user.

    Adds it to the caller's session without committing, so it is saved in the
    same transaction as the change that triggered it (e.g. an order status
    update). The caller commits.
    """
    notification = Notification_Model(user_id=user_id, title=title, message=message)
    db.add(notification)
    return notification
