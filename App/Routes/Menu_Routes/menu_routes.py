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


#=====================Create Pizza (Admin)===================
@menu_router.post("/Create_Pizza",status_code=status.HTTP_200_OK,response_model=Pizza_Response)
def create_pizza(pizza:Pizza_Request,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user.role!="admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can add a new pizza in database !")
    else:
        new_pizza=Pizza_Model(
                name=pizza.name,
                description=pizza.description,
                base_price=pizza.base_price,
                image_url=str(pizza.image_url),
                is_available=pizza.is_available,
                category_id=pizza.category_id
            )

        db.add(new_pizza)
        db.commit()
        db.refresh(new_pizza)
        return new_pizza

#=====================Getting All Pizzas===================
@menu_router.get("/Get_all_pizzas",status_code=status.HTTP_200_OK,response_model=List[Pizza_Response])
def Get_all_pizza(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
        pizzas=db.query(Pizza_Model).all()
        if not pizzas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Pizza is added in Database yet")

        return pizzas

#=====================Getting a Pizza Bt Id===================
@menu_router.get("/Pizza_by_id/{pizza_id}",status_code=status.HTTP_200_OK,response_model=Pizza_Response)
def Pizza_by_id(pizza_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
        pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
        if not pizza:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pizza with this id is not found in database")
        return pizza

#=====================Upate a Pizza (Admin)===================
@menu_router.put("/Update_Pizza/{pizza_id}",status_code=status.HTTP_201_CREATED)
def Update_Pizza(pizza:Pizza_Request,pizza_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user.role!="admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only Admin can Update the Pizza Details !")
    
    db_pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()

    if not db_pizza:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pizza with this id is not found in Data Base !")
    else:
        db_pizza.name = pizza.name
        db_pizza.description = pizza.description
        db_pizza.base_price = pizza.base_price
        db_pizza.image_url = str(pizza.image_url)
        db_pizza.is_available = pizza.is_available
        db_pizza.category_id = pizza.category_id

        db.add(db_pizza)
        db.commit()
        db.refresh(db_pizza)

        return db_pizza

#=====================Delete a Pizza (Admin)===================
@menu_router.delete("/Delete_Pizza/{pizza_id}",status_code=status.HTTP_200_OK)
def Delete_Pizza(pizza_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user.role!="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can delete a pizza from database !")
    else:
        pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
        if pizza is not None:
            try:
                db.delete(pizza)
                db.commit()
                db.refresh(pizza)
                return {"Pizza Deleted Successfully !" : pizza}
            
            except Exception as e:
                db.delete(pizza)
                db.commit()
                return {"Msg":"Pizza Deleted Successfully","Pizza":pizza}
                
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pizza with this Is not found in Database !")

#==================Create Categories in Datavase (Admin)===========================
@menu_router.post("/Create_Category",status_code=status.HTTP_201_CREATED,response_model=Category_Response)
def Create_Category(category:Category_Request,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if user.role!="admin":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Only Admin can add the categories for pizza in DataBase !")
    else:
        new_category=Category_Model(
            name=category.name,
            description=category.description
        )
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category

#=================List All Categories in DataBase===========================
@menu_router.get("/View_Categories",status_code=status.HTTP_200_OK)
def View_Categories(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    categories=db.query(Category_Model).all()
    #.all function return you an empty list in database 
    if not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Category is Added to the Database yet")
    else:
        return categories

