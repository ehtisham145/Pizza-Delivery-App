from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status,APIRouter,Query

from App.Database.database import get_db
from App.Utils.db_helper import safe_commit
from App.Utils.middleware import get_current_user,require_admin
from App.DataModels.Auth_Users.user_model import User
from App.Schemas.Notifications.notification_schema import (
    NotificationListOut,
    NotificationOut,
    UnreadCountOut
)
from App.DataModels.Notifications.notification_model import Notification_Model




notification_router=APIRouter()

#─────────────────────────────────────────────
# Helper: ownership-safe notification fetcher
# ─────────────────────────────────────────────
def _get_notification_or_404(
    notification_id: int, user_id: int,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user),
    )->Notification_Model:

    #1.Getting Notification
    notification=(
        db.query(Notification_Model).filter(
            Notification_Model.id == notification_id,
            Notification_Model.user_id == user.id
        ).first()
    )

    #2.Raise Error For Notification
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Notification with ID {id} not found !")


    return notification

#1.======================Get Notifications============================

@notification_router.get(
    "/get_notifications",
    status_code=status.HTTP_200_OK,
    response_model=NotificationListOut
)
def get_notifications(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    skip = (page - 1) * size
    
    query = db.query(Notification_Model).filter(
        Notification_Model.user_id == user.id)
    
    total = query.count()
    
    notifications = (
        query
        .order_by(Notification_Model.created_at.desc())   # ← FIX 3
        .offset(skip)
        .limit(size)
        .all()
    )

    return {"notifications": notifications, "total": total} 

#2.=======================Mark as Read a Notification===================

@notification_router.patch(
    "/mark_as_read_notification/{notification_id}"
    ,status_code=status.HTTP_200_OK
    ,response_model=NotificationOut
)
def mark_as_read_notification(
    notification_id:int,
    db:Session=Depends(get_db)
    ,user:User=Depends(get_current_user)
):
    notification=_get_notification_or_404(notification_id,user.id,db)

    if notification.is_read:
        return notification
    
    notification.is_read=True
    
    safe_commit(db)
    
    db.refresh(notification)
    
    return notification


#3.======================Mark All Notification as Read===================
@notification_router.patch(
    "/mark_all_notification_as_read",
    status_code=status.HTTP_200_OK,
    response_model=NotificationListOut
)

def mark_all_notification_as_read(
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
    #1.Fetching all Notifications from db
    db.query(Notification_Model).filter(
        Notification_Model.user_id==user.id,
        Notification_Model.is_read==False,
        ).update({"is_read":True},synchronize_session="fetch")

    #2.Saving Changes in Database
    safe_commit(db)    
    
    notifications = (
        db.query(Notification_Model).filter(
            Notification_Model.user_id ==  user.id
        ).order_by(Notification_Model.created_at.desc()).limit(50).all()
    )
    
    total = db.quer(Notification_Model).filter(
        Notification_Model.user_id == user.id
    ).count()

    return {"Notifications":notifications,"total":total}


#4.=====================GET /notifications/unread-count====================
@notification_router.get(
    "/unread/notifications/count",
    status_code=status.HTTP_200_OK,
    response_model=UnreadCountOut
)
def notification_count(
    db:Session=Depends(get_db)
    ,user:User=Depends(get_current_user)
):
    #1.Fetching Notification from db
    count=db.query(Notification_Model).filter(
        Notification_Model.user_id==user.id,Notification_Model.is_read==False
        ).count()
    return {"count":count}