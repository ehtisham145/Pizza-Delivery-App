from App.Database.database import Base,get_db
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status,APIRouter
from App.Utils.middleware import get_current_user,require_admin
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Order.order_model import Order_Model
from App.Schemas.Order.order_schemas import OrderResponseSchema
from App.Schemas.Auth_Users.User_Schema.register_schema import UserResponseSchema 
from App.Utils.constant import OrderStatusEnum
from typing import List
admin_router=APIRouter()

#2.=============================Get All User (Admin)=======================================
@admin_router.get("/get_all_user/admin",status_code=status.HTTP_200_OK,response_model=List[UserResponseSchema])
def get_all_user(db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.Fetching all users
    db_users=db.query(User).all()
    #2.Raise Error if table Empty
    if not db_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No User is Added in Data Base Yet !")
    return db_users
#3.==============================Deactivate a User (Admin)===================================
@admin_router.patch("/deactivate_user/admin/{user_id}",status_code=status.HTTP_200_OK,response_model=UserResponseSchema)
def deactivate_user(user_id:int,db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.Checking user Exists
    db_user=db.query(User).filter(User.id==user_id).first()
    #2.Raise Error if User not Exists
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not Found !")
    #3.Updating User Status
    db_user.is_active="False"
    db.commit()
    db.refresh(db_user)
    return db_user

#4.==============================Activate a User (Admin)===================================
@admin_router.patch("/activate_user/admin/{user_id}",status_code=status.HTTP_200_OK,response_model=UserResponseSchema)
def activate_user(user_id:int,db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.Checking user Exists
    db_user=db.query(User).filter(User.id==user_id).first()
    #2.Raise Error if User not Exists
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not Found !")
    #3.Updating User Status
    db_user.is_active="True"
    db.commit()
    db.refresh(db_user)
    return db_user

#5.============================Change User Role (Admin)==================================
@admin_router.patch("/change_role/admin/{user_id}",status_code=status.HTTP_200_OK,response_model=UserResponseSchema)
def change_role(assign_role:str,user_id:int,db:Session=Depends(get_db),user:User=Depends(require_admin)):
    assign_role=assign_role.lower()
    #1.Checking user Exists
    db_user=db.query(User).filter(User.id==user_id).first()
    #2.Raise Error if User not Exists
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not Found !")
    #3.Check role of new user
    if db_user.role=="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Admin cannot Update Admin Role")
    #4.Updating User Role
    db_user.role=assign_role
    db.commit()
    db.refresh(db_user)

    return db_user
    
#6.============================Get All Order with Filters(Admin)==================================
@admin_router.get("/get_all_orders/admin/{order_status}",status_code=status.HTTP_200_OK,response_model=List[OrderResponseSchema])
def get_all_orders(order_status:OrderStatusEnum,db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.Fetching orders with status
    db_orders=db.query(Order_Model).filter(Order_Model.status==order_status.value).all()
    #2.Raise Error if Order belong to that status not found
    if not db_orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUNDm,detail=f"No {order_status.value} is Found in Database")
    return db_orders