from fastapi import FastAPI
from App.Routes.order_routes import order_router
from App.Routes.auth_routes import auth_router
from App.Routes.pizza_routes import pizza_router
from App.Database.init_db import create_tables
import uvicorn

app=FastAPI()

create_tables()
    
app.include_router(auth_router,prefix='/auth',tags=['Authentication'])
app.include_router(pizza_router,prefix="/oper",tags=["Pizza"])
app.include_router(order_router,prefix="/order",tags=['Order'])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)