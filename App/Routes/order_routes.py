from fastapi import APIRouter,status,Depends,HTTPException
from App.Schemas.order import OrderModel, OrderResponseModel # Ensure in mein validator ho
from App.Database.database import get_db
from sqlalchemy.orm import Session
from App.Database.data_models.order_model import Order
from App.Security.jwt import get_current_user
from App.Database.data_models.user_model import User

order_router = APIRouter()

#--------------------------------Create New Order--------------------------------------------------------

@order_router.post("/Create_Order", response_model=OrderResponseModel, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderModel, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Please Login First !")
    # Order object banana
    new_order = Order(
        quantity=order.quantity,
        order_status=order.order_status,
        pizza_sizes=order.pizza_sizes,
        user_id=current_user.id
    )
    
    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order # Ye Pydantic model ke mutabiq convert ho jayega
    
    except Exception as e:
        db.rollback()
        # Debugging ke liye error print karein
        print(f"Error: {e}") 
        raise HTTPException(status_code=400, detail="Data Entry Become Failed Please Check Model Validation")
    

#--------------------------------------Get all the Orders-------------------------------------------

@order_router.get("/get_all_orders",response_model=list[OrderResponseModel],)
def get_orders(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    orders = db.query(Order).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found in database")
    else:
        return orders