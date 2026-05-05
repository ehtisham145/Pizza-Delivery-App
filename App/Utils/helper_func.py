from App.Database.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from App.DataModels.Notifications.notification_model import Notification_Model

def create_notification(user_id:int, title: str, message: str,db:Session=Depends(get_db),):
    new_notification=Notification_Model(
        user_id=user_id,
        title=title,
        message=message
    )
    db.add(new_notification)
    db.commit()