from fastapi import HTTPException,status,Depends,APIRouter
from sqlalchemy.orm import Session
from App.Schemas.Auth_Users.User_Schema.update_schema import UserUpdateSchema
from App.Schemas.Auth_Users.Password_Schema.change_password_schema import ChangePasswordSchema
from App.Utils.middleware import get_current_user,get_password_hash,verify_password 
from App.DataModels.Auth_Users.user_model import User
from App.Utils.db_helper import safe_commit
from App.Database.database import get_db
import logging
logger=logging.getLogger(__name__)

profile_router=APIRouter()

#1.--------------------Get current user profile----------------------
@profile_router.get(
    "/get-user-profile",
    status_code=status.HTTP_200_OK
    )
def get_profile(current_user:User=Depends(get_current_user)):
    """
    Returns the profile of the currently authenticated user.
    Sensitive fields (e.g. password) are excluded via the response schema.
    """

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


#2.--------------------Update user profile----------------------
@profile_router.put(
    "/update-profile",
    status_code=status.HTTP_200_OK
    )
def update_Profile(
    update_data:UserUpdateSchema,
    current_user:User=Depends(get_current_user),
    db:Session=Depends(get_db)
):
    """
    Updates mutable profile fields (full_name, phone_number).
    Only fields explicitly provided in the request body are changed.
    """

    updated = False

    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
        updated=True
        
    if update_data.phone_number is not None:
        current_user.phone_number = update_data.phone_number
        updated=True
    
    if not updated:
        return {"message": "No changes provided.", "full_name": current_user.full_name}

    try:
        safe_commit(db)
        db.refresh(current_user)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during profile update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update profile. Please try again later.",
        )
 
    return {"message": "Profile updated successfully.", "full_name": current_user.full_name}


#3.------------------Change Your Password-----------------------
@profile_router.put(
    "/change-password",
    status_code=status.HTTP_201_CREATED
)
def ChangePassword(data:ChangePasswordSchema,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    
    """
    Validates the old password, confirms the new password matches its
    confirmation, then replaces it with a fresh bcrypt hash.
    """
    #1.Verify Password
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="In Correct Old Password"
        )
    #2.Validating Password with New Password
    if data.new_password != data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please Match your New and Confirm Passwords !"
        )
   
   #3.Updating Password
    current_user.password = get_password_hash(data.new_password)
    
    safe_commit(db)
    db.refresh(current_user)

    return {"New Password : ": current_user.password}