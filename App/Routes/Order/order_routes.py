from fastapi import APIRouter,HTTPException,Depends,status
from App.Database.database import get_db
from sqlalchemy.orm import Session
from App.Routes.Auth_Users.login_register import get_current_user
from App.DataModels.Order.order_model import Order_Model
from App.DataModels.Cart.cart_model import Cart_Model
from datetime import datetime
from uuid import UUID

#Create Order Router
order_router=APIRouter()

#========================Place Order Of  Customer From Cart====================
@order_router.post("/place_order_from_cart",status_code=status.HTTP_200_OK)
def place_cart_order(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #Check whether the cart belongs to user
    order_id=UUID(order_id)
    cart_user_items=db.query(Cart_Model).filter(Cart_Model.user_id==user.id).all()
    #Raise Error If Cart Related to user is not found
    if not cart_user_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cart is Empty !")
    try:
        #Add the Item to Order Table
        total_amount = sum(item.total_price for item in cart_user_items)
        new_order=Order_Model(
            user_id=user.id,#Foreign  Key
            status="Pending",
            total_price=total_amount,
            created_at=datetime.utcnow(),
            
        )
        #Adding New Item in Order Table
        db.add(new_order)
        db.flush()
        #Removing the Item from Cart
        db.query(Cart_Model).filter(Cart_Model.user_id == user.id).delete(synchronize_session=False)
        db.commit()
        db.refresh(new_order)

        return {
            "status": "success",
            "message": "Order successfully placed!",
            "order_details": {
                "order_id": new_order.id,
                "total_price": new_order.total_price
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction failed. Please try again.")


# GET	/api/v1/orders/my-orders/{id}	Customer	My single order detail
@order_router.get("/order_details/{order_id}",status_code=status.HTTP_200_OK)
def order_details(order_id:str,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    print(f"DEBUG: User ID: {user.id}, Order ID: {order_id}")
    #User order
    user_order=db.query(Order_Model).filter(Order_Model.id==order_id,Order_Model.user_id==user.id,).first()
    #Raise Error
    if not user_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order Not Found !"
        )
    else:
        return user_order