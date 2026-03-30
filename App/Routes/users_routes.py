from fastapi import FastAPI,APIRouter,HTTPException,Depends,status
from App.Database.database import get_db,SessionLocal
from sqlalchemy.orm import Session
from App.Database.data_models.user_model import User
from App.Security.jwt import get_current_user
from typing import List
user_router=APIRouter()

#Get all users in database
@user_router.get("/get_all_user")
def get_users(db:Session=Depends(get_db),current_user: User = Depends(get_current_user)):
    #get all the users from data base
    users=db.query(User).all()

    if not users:
        raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST,detail="No User is present in database !")

    else:
        return users