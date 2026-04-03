from fastapi import HTTPException,status,Depends,APIRouter
from sqlalchemy.orm import Session
from App.Schemas.user_schemas.update_schema import UserUpdateSchema
from App.Security.jwt import get_current_user
from App.DataModels.user_model import User
from App.Database.database import get_db
#--------------------Get current user profile----------------------
profile_router=APIRouter()
@profile_router.get(
    "/Get User Profile",
    status_code=status.HTTP_200_OK,response_model=None
    )
def get_profile(current_user:User=Depends(get_current_user)):
    #Only Show the profile of authenticated users
    return current_user
    
#--------------------Update user profile----------------------
@profile_router.put(
    "/Update_Profile",
    status_code=status.HTTP_200_OK
    )
def Update_Profile(update_data:UserUpdateSchema,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
        
    if update_data.phone_number is not None:
        current_user.phone_number = update_data.phone_number

    db.commit()


    db.refresh(current_user)

    return {"message": "Profile updated successfully", "user": current_user.full_name}