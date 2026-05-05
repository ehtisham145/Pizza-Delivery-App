from App.Database.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status,APIRouter
from App.Utils.middleware import get_current_user,require_admin
from App.Schemas.Notifications.notification_schema import NotificationListOut,NotificationOut,UnreadCountOut
from App.DataModels.Notifications.notification_model import Notification_Model

notification_router=APIRouter()

#1.======================Get Notifications============================
@notification_router.get("/get_notifications",status_code=status.HTTP_200_OK,response_model=NotificationListOut)
def get_notifications(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    skip = (page - 1) * size
    query = db.query(Notification_Model).filter(Notification_Model.user_id == user.id)
    total = query.count()
    notifications = query.offset(skip).limit(size).all()

#2.=======================Mark as Read a Notification===================
@notification_router.patch("/mark_as_read_notification/{notification_id}",status_code=status.HTTP_200_OK,response_model=NotificationOut)
def mark_as_read_notification(notification_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Find Notification in db
    db_notification=db.query(Notification_Model).filter(Notification_Model.id==notification_id).first()
    #2.Raise Error if notification not found
    if not db_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Notification not Found !")
    #3.Updating Status
    db_notification.is_read=True
    db.commit()
    db.refresh(db_notification)
    return db_notification

#3.======================Mark All Notification as Read===================
@notification_router.patch("/mark_all_notification_as_read",status_code=status.HTTP_200_OK,response_model=NotificationListOut)
def mark_all_notification_as_read(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Fetching all Notifications from db
    db_notifications=db.query(Notification_Model).filter(Notification_Model.user_id==user.id).all()
    #2.Updating the status of every single notification
    for notification in db_notifications:
        notification.is_read=True
    db.commit()
    db.refresh(db_notifications)
    return db_notifications

#4.=====================GET /notifications/unread-count====================
@notification_router.get("/unread/notifications/count",status_code=status.HTTP_200_OK,repsonse_model=UnreadCountOut)
def notification_count(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Fetching Notification from db
    count=db.query(Notification_Model).filter(Notification_Model.user_id==user.id,Notification_Model.is_read==False).count()
    return {"Count":count}