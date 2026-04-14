from fastapi import FastAPI,HTTPException,APIRouter,status,Depends,Form
from App.Utils.middleware import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from App.Database.database import get_db
from App.DataModels.Auth_Users.user_model import User
from typing import List
from App.Utils.constant import PizzaCategoryEnum,PizzaSizeEnum
from App.DataModels.Menu_Model.menu_model import Category_Model,Pizza_Model,Size_Model,ToppingModel 
from App.Schemas.Menu.menu_schema import Category_Request,Category_Response,Pizza_Request,Pizza_Response,Size_Response,Size_Request,Topping_Request,Topping_Response 
#Creating a Router for Menu related work
menu_router=APIRouter()


#=====================Create Pizza (Admin)===================
@menu_router.post("/Create_Pizza",status_code=status.HTTP_201_CREATED,response_model=Pizza_Response)
def create_pizza(pizza:Pizza_Request,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Guard Check
    if user.role!="admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can add a new pizza in database !")
    #Existing pizza
    existing_pizza = db.query(Pizza_Model).filter(Pizza_Model.name == pizza.name).first()
    
    if existing_pizza:
        # Agar mil jaye, toh error throw karein
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pizza with this name is already stored in Data Base use another name."
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
    db.commit()
    db.refresh(new_pizza)
    return new_pizza

#=====================Getting All Pizzas===================
@menu_router.get("/Get_all_pizzas",status_code=status.HTTP_200_OK,response_model=List[Pizza_Response])
def Get_all_pizza(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
        pizzas=db.query(Pizza_Model).filter(Pizza_Model.is_available==True).all()
        if not pizzas:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Pizza is added in Database yet")
        #Show only Availble Pizzas
        return pizzas

#=====================Getting a Pizza Bt Id===================
@menu_router.get("/Pizza_by_id/{pizza_id}",status_code=status.HTTP_200_OK,response_model=Pizza_Response)
def Pizza_by_id(pizza_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
        pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
        if not pizza:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pizza with this id is not found in database")
        return pizza

#=====================Upate a Pizza (Admin)===================
@menu_router.put("/Update_Pizza/{pizza_id}",status_code=status.HTTP_200_OK)
def Update_Pizza(pizza:Pizza_Request,pizza_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Guard Check
    if user.role!="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can Update the Pizza Details !")
    
    #2.Searching Pizza in DataBase
    db_pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
    
    #3.Raise Error if pizza not found
    if not db_pizza:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pizza with this id is not found in Data Base !")
    
    #4.Updating Pizza in Data Base
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
#=====================Update Pizza Status (Admin or Staff)===================
@menu_router.put("/Update_Pizza_Status/{pizza_id:int}",status_code=status.HTTP_200_OK)
def Update_Pizza_Status(pizza_data:Pizza_Request,pizza_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Guard Check
    if user.role!="staff" or user.role!="admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only Admin or Staff Memeber can Update Pizza Status !")
    #2.Search for Pizza id
    db_pizza=db.query(Pizza_Model).filter(Pizza_Model.id==pizza_id).first()
    #3.If Pizza not found
    if not db_pizza:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Pizza with this id is not found in data base !")
    #4.Update Pizza Status
    db_pizza.is_available=pizza_data.is_available

    #5.In Data Base
    db.add(db_pizza)
    db.commit()
    db.refresh()

    return db_pizza


#=====================Delete a Pizza (Admin)===================
@menu_router.delete("/pizzas/{pizza_id}", status_code=status.HTTP_200_OK)
def delete_pizza(pizza_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    allowed_roles=["admin","staff"]
    # 1. Authorization Guard
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only Admin can delete a pizza."
        )

    # 2. Fetch the pizza
    pizza = db.query(Pizza_Model).filter(Pizza_Model.id == pizza_id).first()
    
    # 3. Guard: Not Found
    if not pizza:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Pizza with this id is not found in data base"
        )

    # 4. Execution
    # We don't need a try/except here because your main.py handles it!
    Pizza_Model.is_deleted==True
    
    db.commit()
    return {"message": "Pizza deleted successfully"}

#==================Create Categories in Datavase (Admin)===========================
@menu_router.post("/Create_Category",status_code=status.HTTP_201_CREATED,response_model=Category_Response)
def Create_Category(name:PizzaCategoryEnum=Form(...),description: str = Form(None),db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Guard Check
    if user.role!="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can add the categories for pizza in DataBase !")
    
    #2.Create Categories
    new_category=Category_Model(
            name=name,
            description=description
        )
    #3.Adding Category in Database
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

#=================List All Categories in DataBase===========================
@menu_router.get("/View_Categories",status_code=status.HTTP_200_OK)
def View_Categories(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    categories=db.query(Category_Model).all()
    #.All function return you an empty list in database 
    if not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Category is Added to the Database yet")
    else:
        return categories

#=============Create Toppings(only for Admin)==============================
@menu_router.post("/Create_Toppings",status_code=status.HTTP_201_CREATED,response_model=Topping_Response)
def create_topping(topping_data:Topping_Request,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    # Guard 1: Check Role
    if user.role!="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can create toppings !")
    # Guard 2: Check Uniqueness
    existing_topping=db.query(ToppingModel).filter(topping_data.name==ToppingModel.name).first()
    if existing_topping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Topping already exists."
    )# Execution: If we got here, everything is valid
    new_topping=ToppingModel(
                name=topping_data.name,
                extra_price=topping_data.extra_price
            )
    #Adding in Data Base !
    db.add(new_topping)
    db.commit()
    db.refresh(new_topping)
        
    return new_topping

#=============List All Topping==============================
@menu_router.get("/All_Toppings",status_code=status.HTTP_200_OK,response_model=List[Topping_Response])
def get_all_toppings(db:Session=Depends(get_db),user:User=Depends(get_current_user),response_model=List):
    #1. Accessing all topping in database
    toppings=db.query(ToppingModel).all()
    #2.Check whether Toppings are present or not
    if not toppings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Toppings is added by Admin in Data Base !")
    #.3 Show all toppings
    return toppings

#=============Update Topping Only Admin==============================
@menu_router.put("/Update_Topping/{topping_id}")
def Update_Topping(topping_data:Topping_Request,topping_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Guard Check for Admin
    if user.role!="admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only Admin can Update Topping Details in Data Base !")
    #2.Search Topping Id
    db_topping=db.query(ToppingModel).filter(ToppingModel.id==topping_id).first()
    #3.Raise Error if id not found
    if not db_topping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Topping is found with this id in data base !")
    #4.Update Topping
    db_topping.name=topping_data.name
    db_topping.extra_price=topping_data.extra_price
    db_topping.is_available=topping_data.is_available
    #5.Adding in Data base
    db.add(db_topping)
    db.commit()
    db.refresh(db_topping)

    #6.Return Topping
    return db_topping

