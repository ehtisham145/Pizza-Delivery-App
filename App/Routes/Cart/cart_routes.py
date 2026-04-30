from fastapi import Depends,HTTPException,status,APIRouter
from App.Database.database import get_db
from sqlalchemy.orm import Session
from App.Routes.Auth_Users.login_register import get_current_user
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Cart.cart_model import Cart_Model,Cart_Item
from App.DataModels.Menu.menu_model import Pizza_Model,Size_Model
from typing import List
from App.Schemas.Cart.cart_schema import CartResponseSchema,AddToCartSchema
from sqlalchemy.orm import joinedload
#==========================Developing Router for Cart Menu=====================
cart_router=APIRouter()

#======================Customer	Get my cart with all items + total============
@cart_router.get("/get_your_cart", response_model=List[CartResponseSchema])
def get_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Use joinedload to ensure 'items' are fetched along with the cart
    db.expire_all()
    cart_items = db.query(Cart_Model).options(
        joinedload(Cart_Model.items)
    ).filter(Cart_Model.user_id == user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    return cart_items

#====================Update Cart Item Quantity (Customer)=================================
@cart_router.put("/Update_cart_Item_quantity", status_code=status.HTTP_200_OK)
def Update_cart_Item_quantity(quantity: int, item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    
    # 1. Get the user's cart
    user_cart = db.query(Cart_Model).filter(Cart_Model.user_id == user.id).first()

# 2. Update the item inside that specific cart
    db_item = db.query(Cart_Item).filter(
        Cart_Item.id == item_id,
        Cart_Item.cart_id == user_cart.id,
        Pizza_Model.is_deleted == False
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # 2. Update the attribute explicitly
    db_item.quantity = quantity
    db_item.sub_total=db_item.unit_price*quantity

    
    # 3. Mark the object as "dirty" to ensure SQLAlchemy knows it changed
    db.add(db_item) 
    
    try:
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    return db_item

#=================Delete Customer Clear entire cart======================================
@cart_router.delete("/Delete_Entire_Cart",status_code=status.HTTP_200_OK)
def delete_entire_cart(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #Fetching Data from Data Base
    db_cart=db.query(Cart_Model).filter(Cart_Model.user_id==user.id)
    #Return Error
    if not db_cart.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cart is Empty")
    #Deleting Cart from Database
    db_cart.delete(synchronize_session=False)
    db.commit()

    return {"Message":"Your Entire Cart Has Been Cleared !"}

#==================Remove one item From Cart===============================================
@cart_router.delete("/Delete_Cart_Item/{item_id}",status_code=status.HTTP_200_OK)
def delete_cart_item(item_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #Fetching Data from Data Base
    db_cart_item = db.query(Cart_Item).join(Cart_Model).filter(
        Cart_Item.id == item_id,       
        Cart_Model.user_id == user.id    
    ).first()
    #Return Error
    if not db_cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Item not Found in Cart")
    #Deleting Item From Cart Table
    db.delete(db_cart_item)
    db.commit()

    return {"Message":"Item has been deleted from Cart Successfully !"}


#================Add item to cart=========================================================
@cart_router.post("/add_item_to_cart/{item_id}", status_code=status.HTTP_200_OK)
def add_item_to_cart(
    item_id: int, 
    item_data: AddToCartSchema, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    # 1. Fetch Pizza and Size details
    pizza = db.query(Pizza_Model).filter(Pizza_Model.id == item_id).first()
    size_obj = db.query(Size_Model).filter(Size_Model.id == item_data.size_id).first()
    
    if not pizza:
        raise HTTPException(status_code=404, detail="Pizza not found!")
    if not size_obj:
        raise HTTPException(status_code=404, detail="Invalid size selection!")

    # 2. Calculate dynamic prices based on size multiplier
    unit_price = pizza.base_price * size_obj.price_multiplier
    sub_total = unit_price * item_data.quantity

    # 3. Get or Create the User's Cart
    user_cart = db.query(Cart_Model).filter(Cart_Model.user_id == user.id).first()
    if not user_cart:
        user_cart = Cart_Model(user_id=user.id)
        db.add(user_cart)
        db.flush() # Use flush to get the ID without fully committing yet

    # 4. Check if this specific Pizza AND Size combination exists in the cart
    cart_item = db.query(Cart_Item).filter(
        Cart_Item.cart_id == user_cart.id, 
        Cart_Item.pizza_id == item_id,
        Cart_Item.size_id == item_data.size_id
    ).first()

    if cart_item:
        # Update existing item quantity and recalculate sub_total
        cart_item.quantity += item_data.quantity
        cart_item.sub_total = cart_item.quantity * cart_item.unit_price
    else:
        # Create a brand new Cart Item
        new_item = Cart_Item(
            cart_id=user_cart.id,
            pizza_id=item_id,
            size_id=size_obj.id,
            size=size_obj.size,  # FIX: Passing the required string to avoid IntegrityError
            quantity=item_data.quantity,
            unit_price=unit_price,
            sub_total=sub_total
        )
        db.add(new_item)

    # 5. Commit all changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    return {"Message": "Item has been Added to Cart Successfully!"}