from fastapi import FastAPI
from App.Routes.login_register import auth_router
from App.Database.init_db import create_tables
from App.Routes.profile import profile_router
import uvicorn

app=FastAPI()

create_tables()
    
app.include_router(auth_router,prefix='/auth',tags=['Authentication'])
app.include_router(profile_router,prefix="/profile",tags=["Profile"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8004, reload=True)