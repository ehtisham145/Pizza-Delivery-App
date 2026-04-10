from fastapi import FastAPI,HTTPException,APIRouter,status,Depends
from App.Utils.middleware import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from App.Database.database import get_db
from App.DataModels.Auth_Users.user_model import User
from typing import List
from App.DataModels.Menu_Model.menu_model import Category_Model,Pizza_Model,Size_Model 
from App.Schemas.Menu_Schema.menu_schema import Category_Request,Category_Response,Pizza_Request,Pizza_Response,Size_Response,Size_Request 
#Creating a Router for Menu related work
menu_router=APIRouter()

#=====================Getting All Pizzas===================
@menu_router.get("/Get_all_pizzas",status_code=status.HTTP_200_OK,response_model=List[Pizza_Response])
def Get_all_pizza(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    try:
        pizza=db.query(Pizza_Model).all()
        if not pizzas:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No Pizza is added in Database yet")

        return pizzas
    
    #This Error statement is used when error is occured in database connection
    except SQLAlchemyError as e:
        # This catches specific database issues (Connection, Syntax, etc.)
        print(f"Database Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred while fetching pizzas."
        )
    #We will use it for catching other errors
    except Exception as e:
        print(f"Unexpected Error : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An Internal Server error is Occured")