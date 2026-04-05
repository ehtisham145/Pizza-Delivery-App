from fastapi import HTTPException,status,Depends,APIRouter
from sqlalchemy.exc import IntegrityError
from App.DataModels.pizza_model import PizzaModel
from sqlalchemy.orm import Session
from App.Schemas.pizza_schemas import PizzaCreate,PizzaResponse
from App.Security.auth_utils import get_current_user
from App.Database.database import get_db
#----------------------Pizza Router--------------------------------
pizza_router=APIRouter()

#Pizza App 
#----------------------Add a Pizza---------------------------------
@pizza_router.post("/Add_Pizza",status_code=status.HTTP_201_CREATED)
def add_pizza(pizza:PizzaCreate,db:Session=Depends(get_db),current_user:Session=Depends(get_current_user)):
    
    #Check whether the logged in person is admin or not
    if not current_user or not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Access Denied Only Admin can add Pizza !")
    #Adding the data of pizza in db
    new_pizza = PizzaModel(**pizza.model_dump())

    try:
        db.add(new_pizza)
        db.commit()
        db.refresh(new_pizza)

        return {"Message": "Pizza Addded Successfully", "data": new_pizza}
    #check the database constraints validation
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Pizza with name '{pizza.name}' already exists!"
        )
    except Exception as e:
        db.rollback()
        #for debugging
        print(f"Error: {e}") 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An Internal Server Occur While Adding Pizza !")
    

    
#----------------------Update a Pizza-----------------------------------------------------
@pizza_router.put("/update_pizza/{pizza_id}")
def update_pizza(pizza:PizzaCreate,pizza_id:int,db:Session=Depends(get_db),current_user:Session=Depends(get_current_user)):
    #Check whether the logged in person is admin or not
    if not current_user or not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Access Denied Only Admin can Update Pizza !")
    #Record to Find
    pizza_to_update=db.query(PizzaModel).filter(PizzaModel.id == pizza_id).first()
    #Pizza id not found
    if not pizza_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Pizza with ID {pizza_id} not found!"
        )
    try:
        update_data = pizza.model_dump() 
        for key, value in update_data.items():
            setattr(pizza_to_update, key, value)

        db.commit()
        db.refresh(pizza_to_update)
        return {
            "Message": "Pizza Updated Successfully!", 
            "updated_record": pizza_to_update
        }
    #Unique Constraints in Database
    except IntegrityError:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail=f"Update failed: A pizza with the name '{pizza.name}' already exists!"
        )
    except Exception as e:
        db.rollback()
        print(f"Error:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred while adding the pizza.")
    



#------------------------Get All Pizzas----------------------------
@pizza_router.get("/get_all")
def get_all_pizza(db:Session=Depends(get_db),current_user:Session=Depends(get_current_user)):
    #Check whether the logged in person is admin or not
    if not current_user or not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Access Denied Only Admin can View All Pizza !")
    
    # Database query
    pizza_list = db.query(PizzaModel).all()
    
    if not pizza_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pizzas found in the database. Please add some first!"
        )
    
    return pizza_list
    





#----------------------Delete a Pizza--------------------------
@pizza_router.delete("/delete_pizza/{pizza_id}")
def delete_pizza(pizza_id:int,db:Session=Depends(get_db),current_user:Session=Depends(get_current_user)):
    #Check whether the logged in person is admin or not
    if not current_user or not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Access Denied Only Admin can delete Pizza !")
    #record to delete
    pizza_to_delete=db.query(PizzaModel).filter(PizzaModel.id==pizza_id).first()
    #record not found
    if not pizza_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Pizza is found against this Id")
    try: 
        db.delete(pizza_to_delete)
        db.commit()
        return {"Messgae":"Pizza deleted successfully"}
    
    except Exception as e:
        db.rollback()
        print(f"Error {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal Server Error Occur while deleting Pizza !")
    