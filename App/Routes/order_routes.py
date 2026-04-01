from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from App.Schemas.order_schemas import OrderModel, OrderResponseModel
from App.Database.database import get_db
from App.DataModels.order_model import Order
from App.Security.jwt import get_current_user
from App.DataModels.user_model import User

# Initializing the router with a prefix and tags for better documentation
order_router = APIRouter()

# ----------------------------------------------------------------------------------
# CREATE NEW ORDER
# ----------------------------------------------------------------------------------

@order_router.post(
    "/create", 
    response_model=OrderResponseModel, 
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order_data: OrderModel, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new pizza order.
    The user_id is automatically extracted from the JWT token.
    """
    
    # Check if user is authenticated (usually handled by the dependency itself)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Authentication required. Please login."
        )

    # Create new Order instance using dictionary unpacking
    # exclude_unset=True ensures we only use data provided in the request
    new_order = Order(
        **order_data.model_dump(exclude={"user_id"}),
        user_id=current_user.id
    )

    try:
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order
        
    except SQLAlchemyError as e:
        db.rollback()
        # Log the specific database error for debugging
        print(f"Database Integrity Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create order. Please verify your data constraints."
        )
    except Exception as e:
        db.rollback()
        print(f"Unexpected Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )

# ----------------------------------------------------------------------------------
# GET ALL ORDERS (ADMIN ONLY)
# ----------------------------------------------------------------------------------

@order_router.get(
    "/all", 
    response_model=List[OrderResponseModel]
)
def get_all_orders(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all orders from the database.
    Restricted to Admin users only.
    """
    
    # Role-Based Access Control: Only admins should see all orders
    # Assuming your User model has an 'is_admin' or 'role' field
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )

    orders = db.query(Order).all()
    
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No orders found in the system."
        )
    
    return orders