from App.Routes.login_register import auth_router
from fastapi import HTTPException,status
from App.Schemas.user_schemas.register_schema import UserResponseSchema

#--------------------Get current user profile----------------------
@auth_router.get(
    "/Get Profile",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK
    )
def get_profile():
    pass
