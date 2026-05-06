from fastapi import FastAPI,Request,status
from App.Database.init_db import create_tables
from App.Routes.Auth_Users.login_register import auth_router
from App.Routes.Auth_Users.profile import profile_router
from App.Routes.Menu.menu_routes import menu_router
from App.Routes.Cart.cart_routes import cart_router
from App.Routes.Order.order_routes import order_router
from App.Routes.Delivery.delivery_routes import delivery_router
from App.Routes.Payment.payment_routes import payment_router
from App.Routes.Reviews.reviews_routes import review_router
from App.Routes.Admin.admin_routes import admin_router
from App.Routes.Notification.notification_routes import notification_router

from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from fastapi.responses import JSONResponse
from App.Utils.exception_handler import add_exception_handlers
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
app.include_router(delivery_router,prefix="/delivery",tags=["Delivery"])
app.include_router(payment_router,prefix="/payment",tags=["Payment"])
app.include_router(review_router,prefix="/review",tags=["Reviews"])
app.include_router(notification_router,prefix="/notifications",tags=["Notifications"])
app.include_router(admin_router,prefix="/admin",tags=["Admin"])

#==================Running your Server======================
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)

