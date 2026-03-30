from fastapi import HTTPException,status,Depends,APIRouter
from App.Database.data_models.pizza_model import PizzaModel
from sqlalchemy.orm import Session
from App.Schemas.pizza import PizzaCreate,PizzaResponse
from App.Security.jwt import get_current_user
from App.Database.database import get_db
#----------------------Pizza Router--------------------------
pizza_router=APIRouter()

@pizza_router.post("/Add_Pizza",status_code=status.HTTP_201_CREATED)
def add_pizza(pizza:PizzaCreate,db:Session=Depends(get_db),current_user:Session=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Please Login First !")
    
    #Check whether the logged in person is admin or not
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can add pizza !")
    
    new_pizza=PizzaModel(
        name=pizza.name,
        price=pizza.price,
        description=pizza.description,
        size=pizza.size,
        category=pizza.category,
        is_available=pizza.is_available
    )

    try:
        db.add(new_pizza)
        db.commit()
        db.refresh(new_pizza)

        return {"Message": "Pizza Addded Successfully", "data": new_pizza}

    except Exception as e:
        db.rollback()
        #for debugging
        print(f"Error: {e}") 
        raise HTTPException(status_code=400, detail="Data Entry Become Failed Please Check Model Validation")
    