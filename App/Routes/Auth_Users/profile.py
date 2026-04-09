from fastapi import HTTPException,status,Depends,APIRouter
from sqlalchemy.orm import Session
from App.Schemas.Auth_Users.User_Schema.update_schema import UserUpdateSchema
from App.Schemas.Auth_Users.Password_Schema.change_password_schema import ChangePasswordSchema
from App.Utils.middleware import get_current_user,get_password_hash,verify_password 
from App.DataModels.Auth_Users.user_model import User
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
    "/Update Profile",
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




#------------------Change Your Password-----------------------
@profile_router.put(
    "/Change Password",
    status_code=status.HTTP_201_CREATED
)
def ChangePassword(data:ChangePasswordSchema,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="In Correct Old Password"
        )
    
    if data.new_password != data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please Match your New and Confirm Passwords !"
        )
   
    current_user.password = get_password_hash(data.new_password)
    
    db.commit()
    db.refresh(current_user)

    return {"New Password : ": current_user.password}