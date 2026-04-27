from fastapi import FastAPI,Request,status
from App.Database.init_db import create_tables
from App.Routes.Auth_Users.login_register import auth_router
from App.Routes.Auth_Users.profile import profile_router
from App.Routes.Menu.menu_routes import menu_router
from App.Routes.Cart.cart_routes import cart_router
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from fastapi.responses import JSONResponse
from App.Utils.exception_handler import add_exception_handlers
from App.Routes.Order.order_routes import order_router
import uvicorn

#=====================Creating App===================
app=FastAPI()

#===============Running Data base Tables==============
create_tables()

#================Error Handling in main.py==================

add_exception_handlers(app)

#================Including Router in main.py===============    

app.include_router(auth_router,prefix='/auth',tags=['Authentication'])
app.include_router(profile_router,prefix="/profile",tags=["Profile"])
app.include_router(menu_router,prefix="/menu",tags=["Menu Management"])
app.include_router(cart_router,prefix="/cart",tags=["Cart"])
app.include_router(order_router,prefix="/order",tags=["Order"])

#==================Running your Server======================
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)

