from fastapi import FastAPI,HTTPException,APIRouter,status,Depends,Body
from App.Utils.middleware import (
    get_current_user,
    require_admin,
    require_admin_or_staff
)
from App.Utils.db_helper import safe_commit
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from App.Database.database import get_db
from App.DataModels.Auth_Users.user_model import User
from typing import List
from App.Utils.constant import PizzaCategoryEnum,PizzaSizeEnum
from App.DataModels.Menu.menu_model import (
    Category_Model,Pizza_Model,Size_Model,
    Topping_Model
) 
from App.Schemas.Menu.menu_schema import (
     Category_Request,Category_Response,Pizza_Request,
     Pizza_Response,Size_Response,Size_Request,
     Topping_Request,Topping_Response,Update_Pizza_Status 
)
#Creating a Router for Menu related work
menu_router=APIRouter()


#1.=====================Create Pizza (Admin)===================
@menu_router.post("/Create_Pizza",status_code=status.HTTP_201_CREATED,response_model=Pizza_Response)
def create_pizza(pizza:Pizza_Request,db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.
    if db.query(Pizza_Model).filter(Pizza_Model.name == pizza.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pizza with this name already exists.",
        )
    #2.Creating Pizza
    new_pizza=Pizza_Model(
                name=pizza.name,
                description=pizza.description,
                base_price=pizza.base_price,
                image_url=str(pizza.image_url),
                is_available=pizza.is_available,
                category_id=pizza.category_id,
            )
    #3.Adding Pizza in Database
    db.add(new_pizza)
    safe_commit(db)
    db.refresh(new_pizza)
    return new_pizza

#2.=====================Getting All Pizzas===================
@menu_router.get("/Get_all_pizzas",status_code=status.HTTP_200_OK,response_model=List[Pizza_Response])
def Get_all_pizza(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
        pizzas=db.query(Pizza_Model).all()
        if not pizzas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Pizza is added in Database yet")
        #Show only Availble Pizzas
        return pizzas

#=====================Getting a Pizza Bt Id===================
@menu_router.get("/Pizza_by_id/{pizza_id}",status_code=status.HTTP_200_OK,response_model=Pizza_Response)
def Pizza_by_id(pizza_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
        pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
        if not pizza:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Pizza with ID {pizza_id} is not found in database")
        return pizza

#=====================Upate a Pizza (Admin)===================
@menu_router.put("/Update_Pizza/{pizza_id}",status_code=status.HTTP_200_OK)
def Update_Pizza(pizza:Pizza_Request,pizza_id:int,db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.Searching Pizza in DataBase
    db_pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
    
    #2.Raise Error if pizza not found
    if not db_pizza:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Pizza with this {pizza_id} is not found in Data Base !")
    
    #3.Updating Pizza in Data Base
    db_pizza.name = pizza.name
    db_pizza.description = pizza.description
    db_pizza.base_price = pizza.base_price
    db_pizza.image_url = str(pizza.image_url)
    db_pizza.is_available = pizza.is_available
    db_pizza.category_id = pizza.category_id

    db.add(db_pizza)
    safe_commit(db)
    db.refresh(db_pizza)

    return db_pizza


#=====================Update Pizza Status (Admin or Staff)===================
@menu_router.patch("/Update_Pizza_Status/{pizza_id:int}",status_code=status.HTTP_200_OK)
def Update_Pizza_Status(pizza_data:Update_Pizza_Status,pizza_id:int,db:Session=Depends(get_db),user:User=Depends(require_admin_or_staff)):
    db_pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
    #1.If Pizza not found
    if not db_pizza:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Pizza with ID {pizza_id}is not found in data base !")
    #2.Update Pizza Status
    db_pizza.is_available=pizza_data.is_available

    #3.In Data Base
  
    safe_commit(db)
    db.refresh(db_pizza)

    return db_pizza


#===================== Delete Pizza (Admin/Staff Only) ===================
@menu_router.delete("/pizzas/{pizza_id}", status_code=status.HTTP_200_OK)
def delete_pizza(pizza_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin_or_staff)):
    # 1. Database Lookup: Fetch the specific pizza record
    pizza = db.query(Pizza_Model).filter(Pizza_Model.id == pizza_id).first()
    
    #2. Validation Guard: Check if the resource exists
    if not pizza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Pizza with ID {pizza_id} was not found."
        )

    #3.Deleting Pizza
    db.delete(pizza)

    #4. Persistence: Commit changes to the database
    safe_commit(db)
    
    return {"message": f"Pizza {pizza_id} deleted successfully."}




#-------------------------------Categories----------------------------

#==================Create Categories in Datavase (Admin)===========================
@menu_router.post("/Create_Category",status_code=status.HTTP_201_CREATED,response_model=Category_Response)
def Create_Category(name:PizzaCategoryEnum= Body(...),description: str=Body(...),db:Session=Depends(get_db),user:User=Depends(require_admin)):    
    #1.Create Categories
    new_category=Category_Model(
            name=name,
            description=description
        )
    #2.Adding Category in Database
    db.add(new_category)
    safe_commit(db)
    db.refresh(new_category)
    return new_category


#=================List All Categories in DataBase===========================
@menu_router.get("/View_Categories",status_code=status.HTTP_200_OK)
def View_Categories(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    categories=db.query(Category_Model).all()
    #.All function return you an empty list in database 
    if not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Category Added Yet !")

    return categories






#----------------------------------Toppings-----------------------------------


#=============Create Toppings(only for Admin)==============================
@menu_router.post("/Create_Toppings",status_code=status.HTTP_201_CREATED,response_model=Topping_Response)
def create_topping(topping_data:Topping_Request,db:Session=Depends(get_db),user:User=Depends(require_admin)):
    # 1.Check Uniqueness
    if db.query(Topping_Model).filter(Topping_Model.name == topping_data.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Topping already exists.")
    
    #2. Execution: If we got here, everything is valid
    new_topping=Topping_Model(
                name=topping_data.name,
                extra_price=topping_data.extra_price
            )
    
    # 3. Adding in Data Base !
    db.add(new_topping)
    safe_commit(db)
    db.refresh(new_topping)
        
    return new_topping

#=============List All Topping==============================
@menu_router.get("/All_Toppings",status_code=status.HTTP_200_OK,response_model=List[Topping_Response])
def get_all_toppings(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1. Accessing all topping in database
    toppings=db.query(Topping_Model).all()
    #2.Check whether Toppings are present or not
    if not toppings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Toppings is added Yet")
    #.3 Show all toppings
    return toppings

#=============Update Topping Only Admin==============================
@menu_router.put("/Update_Topping/{topping_id}")
def Update_Topping(topping_data:Topping_Request,topping_id:int,db:Session=Depends(get_db),user:User=Depends(require_admin_or_staff)):
    #1.Search Topping Id
    db_topping=db.query(Topping_Model).filter(Topping_Model.id==topping_id).first()
    #2.Raise Error if id not found
    if not db_topping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Topping is found with this id in data base !")
    #3.Update Topping
    db_topping.name=topping_data.name
    db_topping.extra_price=topping_data.extra_price
    db_topping.is_available=topping_data.is_available
    #4.Adding in Data base
    db.add(db_topping)
    safe_commit(db)
    db.refresh(db_topping)

    #5.Return Topping
    return db_topping

