from fastapi import APIRouter,HTTPException,Depends,status,Query
from sqlalchemy.orm import Session,joinedload,selectinload
from datetime import datetime,timedelta,timezone
from typing import List
from typing import Optional
import logging
from fastapi import Form
import logging

logger = logging.getLogger(__name__)

from App.Database.database import get_db
from App.Utils.middleware import (
get_current_user,require_admin,
get_user_or_404,
require_admin_or_staff
)

from App.Utils.db_helper import safe_commit
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Order.order_model import Order_Model,Order_Item_Model
from App.DataModels.Cart.cart_model import Cart_Model,Cart_Item
from App.DataModels.Menu.menu_model import Pizza_Model
from App.DataModels.Delivery.delivery_model import Delivery_Model
from App.Schemas.Order.order_schemas import (
 OrderResponseSchema,
 OrderItemSchema,
 OrderStatusUpdateSchema,
 PlaceOrderSchema
)
from App.Schemas.Order.order_schemas import OrderHistorySchema,OrderStatusUpdateSchema
from App.Utils.validator import validate_uuid
from App.Utils.constant import OrderStatusEnum
from App.Utils.db_helper import safe_commit

#------------------------------Create Order Router--------------------------------
order_router=APIRouter()

#1)=================================Place Order From Cart===============================

@order_router.post(
    "/place_order_from_cart/user"
    ,status_code=status.HTTP_201_CREATED
)
def place_order_from_cart(
    payload:PlaceOrderSchema,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
    
    #1.Validate Address Belongs to User or Not
    address=db.query(Delivery_Model).filter(
        Delivery_Model.id==payload.address_id,
        Delivery_Model.user_id==user.id
    ).first()

    #2.Raise Error If Address Not Found
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Delivery Address Does not found or not belong to you !")
    
    # 3.Fetch Cart and User in a single query
    user_cart=(db.query(Cart_Model).options(
        joinedload(Cart_Model.items)).filter(
            Cart_Model.user_id==user.id
        ).first()
    )

    #4.Raise Error If Cart donot belongs to User
    if not user_cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Cart not found !")

    #5.Cart Item
    cart_items = user_cart.items  # already loaded, no extra query
    
    #6.Raise Error if not item found in Cart
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty!")
        
    pizza_ids={item.pizza_id for item in cart_items}

    pizzas = (
        db.query(Pizza_Model)
        .filter(Pizza_Model.id.in_(pizza_ids))
        .all()
    )
    pizza_map = {pizza.id: pizza for pizza in pizzas}

     #7. Validate every pizza still exists before touching the DB
    missing = pizza_ids - pizza_map.keys()
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Some items in your cart are no longer available (pizza IDs: {missing}). "
                   "Please update your cart.",
        )

    try:
        #8.Total Price
        total_amount=sum(item.unit_price*item.quantity for item in cart_items)
        #9.New Order
        new_order=Order_Model(
            user_id=user.id,
            status="Pending",
            address_id=payload.address_id,
            notes=payload.notes,
            total_price=total_amount,
            created_at=datetime.now(timezone.utc)
        )
        #10.Adding New order in Database
        db.add(new_order)
        db.flush()
        #11.Placing Cart Items in Order Items Table
        db.bulk_save_objects([
            Order_Item_Model(
                order_id=new_order.id,
                pizza_id=item.pizza_id,
                pizza_name=pizza_map[item.pizza_id].name,  #
                size_name=item.size,
                quantity=item.quantity,
                unit_price=item.unit_price,
                sub_total=item.unit_price * item.quantity
            )
            for item in cart_items
        ])
    # 11. Delete cart items in bulk instead of one by one
        for item in cart_items:
            db.delete(item)
        db.delete(user_cart)
        safe_commit(db)

        return {
                "status": "success",
                "message": "Order successfully placed!",
                "order_details": {
                    "order_id": new_order.id,
                    "total_price": new_order.total_price
                }
            }
    except HTTPException:
        raise #lets Fast API handle this Endpoint
   
    #12.Raise Error
    except Exception as e:
       logging.exception(f"Order placement failed for user {user.id}: {e}")
       raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Order could not be placed. Please try again.",
        )



#2)============================Get Order By Order ID User==============================

@order_router.get(
    "/get_order_by_id/user/{order_id}"
    ,status_code=status.HTTP_200_OK,
    response_model=OrderResponseSchema
)
def get_order_by_id(
    order_id:str,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
    #1.Fetching user order    
    user_order=db.query(Order_Model).options(selectinload(Order_Model.order_item
    ).selectinload(Order_Item_Model.pizza)).filter(
         Order_Model.id == str(order_id),
        Order_Model.user_id == user.id 
    ).first()
    
    #2.Raise Error if order not found
    if not user_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not Found")
   
    return user_order



#3)=================================Get All Orders (Only Admin or Staff)==================================

@order_router.get(
    "/get_all_orders/admin",
    status_code=status.HTTP_200_OK,
    response_model=List[OrderResponseSchema]
)
def get_all_orders_admin(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Results per page"),
    order_status: Optional[str] = Query(default=None, description="Filter by order status"),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)           
):
    #1.Fetch Orders From Order Table
    offset = (page - 1) * page_size 
    query=db.query(Order_Model).options(selectinload(Order_Model.order_item)
    .selectinload(Order_Item_Model.pizza))
    #2.apply status If provided
    if order_status:
        query=query.filter(Order_Model.status == order_status)

    #3.Fetching all Orders
    all_orders = (
        query
        .order_by(Order_Model.created_at.desc())   # ✅ newest first — almost always what admin wants
        .offset(offset)
        .limit(page_size)
        .all()
    )

    #4.Return all Order
    return all_orders




#4)===========================Get Order by ID (Admin or Staff)==============================

@order_router.get(
    "/admin/get_orders/{order_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponseSchema
)

def admin_get_order(
    order_id:str,
    db:Session=Depends(get_db),
    user:User=Depends(require_admin_or_staff)
):
    #1.Fetching user order
    user_order=db.query(Order_Model).options(selectinload(Order_Model.order_item)
    .selectinload(Order_Item_Model.pizza)
    ).filter(
        Order_Model.id==order_id
    ).first()
    return user_order




#5)=========================Update Order Status(Admin or Staff)================

@order_router.patch(
    "/update_order_status/admin/{order_id}"
    ,status_code=status.HTTP_200_OK,
    response_model=OrderResponseSchema
)
def update_order_status(
    order_id:str,
    payload: OrderStatusUpdateSchema,
    db:Session=Depends(get_db),
    user:User=Depends(require_admin_or_staff)
):
    #1.Fetch Order from db
    db_order=db.query(Order_Model).filter(Order_Model.id==str(order_id)).first()

    #2.Raise Error If order not found
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Order with ID {order_id} not Found!"
)
   
   #3. Logical Constraint
    if db_order.status == OrderStatusEnum.DELIVERED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a delivered order — it is already in a terminal state"
        )
    

    #5.Updating Status
    db_order.status=payload.new_status.value
    safe_commit(db)

    return db_order



#6)=======================Cancel Order If pending===========================

@order_router.patch(
    "/cancel_Order/User/{order_id}"
    ,status_code=status.HTTP_200_OK,
    response_model=OrderResponseSchema
)
def cancel_order(
    order_id:str,
    db:Session=Depends(get_db)
    ,user:User=Depends(get_current_user)
):
    #1.Query for Order
    user_order=db.query(Order_Model).filter(
        Order_Model.id==order_id).first()
    
    #2.Raise Error
    if not user_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Order with ID {order_id} Not Found")

    #3.Any Other User cannot Cancel any other Order
    if user_order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to cancel this order"
        )

    #4. Check Status
    if user_order.status!= OrderStatusEnum.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be cancelled because its current status is '{user_order.status}'"
        )
    
    #5.Updating Status
    user_order.status=OrderStatusEnum.CANCELLED.value
    safe_commit(db)
    db.refresh(user_order)
    return user_order


#7)========================Track_Order_History/User===============================

@order_router.get(
    "/get_orders_history/user",
    status_code=status.HTTP_200_OK,
    response_model=OrderHistorySchema
)
def get_orders_history(
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
    #1.Fetching User Order
    user_orders=db.query(User).options(selectinload(User.order).selectinload
    (Order_Model.order_item)).filter(
    User.id==user.id
    ).first()

    #2.Return Order
    if not user_orders:
        return []
        
    return user_orders


    