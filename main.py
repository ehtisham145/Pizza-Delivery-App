from fastapi import FastAPI,Request,status
from App.Routes.Auth_Users.login_register import auth_router
from App.Database.init_db import create_tables
from App.Routes.Auth_Users.profile import profile_router
from App.Routes.Menu_Routes.menu_routes import menu_router
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
import uvicorn

#=====================Creating App===================
app=FastAPI()

#===============Running Data base Tables==============
create_tables()

#================Error Handling in main.py==================
@app.exception_handler(SQLAlchemyError) # For DataBase related error
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    print(f"Database Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database connection error occurred."}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Global Unexpected Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

#================Including Router in main.py===============    
app.include_router(auth_router,prefix='/auth',tags=['Authentication'])
app.include_router(profile_router,prefix="/profile",tags=["Profile"])
app.include_router(menu_router,prefix="/menu",tags=["Menu"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)