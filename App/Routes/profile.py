from fastapi import HTTPException,status,Depends,APIRouter
from sqlalchemy.orm import Session
from App.Schemas.user_schemas.register_schema import UserResponseSchema
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
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Please Log in to your Account in order to Access This End point")
    else:
        user_profile_details={
        "Name":current_user.full_name,
        "Email":current_user.email,
        "Password":current_user.password,
        "Phone_number":current_user.phone_number,
        "Role":current_user.role
        }
        
    return user_profile_details
    
    
