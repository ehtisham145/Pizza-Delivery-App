from fastapi import APIRouter,HTTPException,Depends,status
from App.Database.database import get_db
from sqlalchemy.orm import Session,joinedload
from App.Utils.middleware import get_current_user,require_admin
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Order.order_model import Order_Model,Order_Item_Model
from App.DataModels.Cart.cart_model import Cart_Model,Cart_Item
from App.DataModels.Menu.menu_model import Pizza_Model
from datetime import datetime
from App.Schemas.Order.order_schemas import OrderResponseSchema,OrderItemSchema,OrderStatusUpdateSchema
from uuid import UUID
from App.Utils.constant import OrderStatusEnum
from typing import List
from App.Utils.validator import validate_uuid
from fastapi import Form
from App.Schemas.Order.order_schemas import OrderHistorySchema
#Create Order Router
order_router=APIRouter()

#1)=================================Place Order From Cart===============================
@order_router.post("/place_order_from_cart/user",status_code=status.HTTP_201_CREATED)
def place_order_from_cart(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Check Whether the Cart belongs to User
    user_cart=db.query(Cart_Model).filter(Cart_Model.user_id==user.id).first()
    #2.Raise Error If Cart donot belongs to User
    if not user_cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cart not found !")
    #3.Checking Items in Cart
    cart_items=db.query(Cart_Item).filter(Cart_Item.cart_id==user_cart.id).all()
    #4.Raise Error If no Cart Item is Present
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cart is Empty !")
        
    try:
        #5.Total Price
        total_amount=sum(item.unit_price*item.quantity for item in cart_items)
        #6.New Order
        new_order=Order_Model(
            user_id=user.id,
            status="Pending",
            total_price=total_amount,
            created_at=datetime.utcnow()
        )
        #7.Adding New order in Database
        db.add(new_order)
        db.flush()
        #8.Placing Cart Items in Order Items Table
        for cart_item in cart_items:
            pizza_data = db.query(Pizza_Model).filter(Pizza_Model.id == cart_item.pizza_id).first()
            new_order_item = Order_Item_Model(
                    order_id=new_order.id,          
                    pizza_id= cart_item.pizza_id,  
                    size_name=cart_item.size,  
                    pizza_name=pizza_data.name,     
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    sub_total=cart_item.unit_price*cart_item.quantity
                )
            #9.Adding new item in database
            db.add(new_order_item)
            #10.Deleting it from cart item
            db.delete(cart_item)

        db.delete(user_cart)
        db.commit()

        return {
                "status": "success",
                "message": "Order successfully placed!",
                "order_details": {
                    "order_id": new_order.id,
                    "total_price": new_order.total_price
                }
            }
    #10.Raisae Error
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


#2)============================Get Order By Order_ID==============================
@order_router.get("/get_order_by_id/user/{order_id}",status_code=status.HTTP_200_OK,response_model=OrderResponseSchema)
def get_order_by_id(order_id:str,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #2.Fetching user order
    user_order=db.query(Order_Model).options(joinedload(Order_Model.order_item_relationship).joinedload(Order_Item_Model.pizza_relationship)).filter(
        Order_Model.id==order_id,
        Order_Model.user_id==user.id
    ).first()
    #Code in SQL 
    #SELECT orders,order_items,pizza FROM orders 
    # LEFT JOIN order.id==order_items.order_id 
    # LEFT JOIN order_items.pizza_id WHERE order.id==valid_order_id AND order.user_id==user.id 
    #Raise Error If user Order dont exists
    if not user_order:
        print(user.id)
        print(order_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not Found")
    return user_order


#3)=================================Get All Orders (Only Admin or Staff)==================================
@order_router.get("/Get_all_Orders/Admin",status_code=status.HTTP_200_OK,response_model=List[OrderResponseSchema])
def Get_all_Orders_admin(db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.Fetch Orders From Order Table
    all_orders = db.query(Order_Model).options(
        joinedload(Order_Model.order_item_relationship).joinedload(Order_Item_Model.pizza_relationship)
    ).all()
    #2.Raise Error if no record is found
    if not all_orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No order is added in Database yet")

    #3.Return all Order
    return all_orders

#4)===========================Get Order by ID (Admin or Staff)==============================
@order_router.get("/admin/get_orders/{order_id}",status_code=status.HTTP_200_OK,response_model=OrderResponseSchema)
def admin_get_order(order_id:str,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    allowed_roles=["admin","staff"] 
    if user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only Admin or Staff can Access All the Order Details !")
    #2.Fetching user order
    user_order=db.query(Order_Model).options(joinedload(Order_Model.order_item_relationship).joinedload(Order_Item_Model.pizza_relationship)).filter(
        Order_Model.id==order_id
    ).first()
    #Code in SQL 
    #SELECT orders,order_items,pizza FROM orders 
    # LEFT JOIN order.id==order_items.order_id 
    # LEFT JOIN order_items.pizza_id WHERE order.id==valid_order_id AND order.user_id==user.id 
    #Raise Error If user Order dont exists
    if not user_order:
        print(user.id)
        print(order_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not Found")
    return user_order


#5)=========================Update Order Status(Admin or Staff)================
@order_router.patch("/Update_Order_Status/Admin/{order_id}",status_code=status.HTTP_200_OK,response_model=OrderResponseSchema)
def Update_Order_Status(order_id:str,new_status: OrderStatusEnum,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #2.Check the Role
    allowed_roles=["admin","staff"]
    if user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin or Staff can Access All the Order Details !")
    
    #3.Fetch Order from db
    db_order=db.query(Order_Model).filter(Order_Model.id==order_id).first()

    #4.Raise Error If order not found
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Order is Found against this ID !")
   # 5. Logical Constraint
    if db_order.status == "Delivered":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update a delivered order!")

    # 6. Final Update (Only if status is different)
    if db_order.status != new_status:
        db_order.status = new_status.value
        db.commit()
        db.refresh(db_order)
    
    return db_order
    
#6)=======================Cancel Order If pending===========================
@order_router.patch("/Cancel_Order/User/{order_id}",status_code=status.HTTP_200_OK,response_model=OrderResponseSchema)
def Cancel_Order(order_id:str,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #2.Query for Order
    user_order=db.query(Order_Model).filter(Order_Model.id==order_id).first()
    #3.Raise Error
    if not user_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order Not Found")
    #4. Check Status
    if user_order.status.upper() == "PENDING":
        #5.Updating Status
        user_order.status="CANCELLED"
        db.commit()
        db.commit()
        db.refresh(user_order)
        return user_order
    else:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Order cannot be cancelled because its current status is {user_order.status}"
        )
#7)========================Track_Order_History/User===============================
@order_router.get("/Get_Orders_History/User",status_code=status.HTTP_200_OK,response_model=OrderHistorySchema)
def Get_Orders_History(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    user_orders=db.query(User).options(joinedload(User.order_relationship).joinedload(Order_Model.order_item_relationship)).filter(
        User.id==user.id
    ).first()
    #4.Raise Error if Order not found
    if not user_orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Orders not found for this user in database !")
        
    return user_orders


    