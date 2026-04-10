from fastapi import FastAPI,HTTPException,APIRouter,status,Depends
from App.Utils.middleware import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from App.Database.database import get_db
from App.DataModels.Auth_Users.user_model import User
from typing import List
from App.DataModels.Menu_Model.menu_model import Category_Model,Pizza_Model,Size_Model 
from App.Schemas.Menu.menu_schema import Category_Request,Category_Response,Pizza_Request,Pizza_Response,Size_Response,Size_Request 
#Creating a Router for Menu related work
menu_router=APIRouter()

#=====================Getting All Pizzas===================
@menu_router.get("/Get_all_pizzas",status_code=status.HTTP_200_OK,response_model=List[Pizza_Response])
def Get_all_pizza(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    try:
        pizzas=db.query(Pizza_Model).all()
        if not pizzas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Pizza is added in Database yet")

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


#=====================Getting a Pizza Bt Id===================
@menu_router.get("/Pizza_by_id/{pizza_id}",status_code=status.HTTP_200_OK,response_model=Pizza_Response)
def Pizza_by_id(pizza_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    try:
        pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
        if not pizza:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pizza with this id is not found in database")
        return pizza

    except SQLAlchemyError as e:
        # This catches specific database issues (Connection, Syntax, etc.)
        print(f"Database Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred while fetching pizzas."
        )
    except Exception as e:
         print(f"Unexpected Error : {e}")
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An Internal Server error is Occured")


#=====================Create Pizza Only Admin can do it===================
@menu_router.post("/Create_Pizza",status_code=status.HTTP_200_OK,response_model=Pizza_Response)
def create_pizza(pizza:Pizza_Request,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    try:
        if user.role!="admin":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only Admin can add a new pizza in database !")
        
        else:
            new_pizza=Pizza_Model(
                name=pizza.name,
                description=pizza.description,
                base_price=pizza.base_price,
                image_url=pizza.image_url,
                is_available=pizza.is_available,
                category_id=pizza.category_id
            )

            db.add(new_pizza)
            db.commit(new_pizza)
            db.refresh(new_pizza)
            return new_pizza

    except SQLAlchemyError as e:
         # This catches specific database issues (Connection, Syntax, etc.)
        print(f"Database Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        print(f"Unexpected Error : {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An Internal Server error is Occured")
