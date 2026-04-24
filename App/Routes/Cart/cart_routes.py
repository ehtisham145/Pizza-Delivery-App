from fastapi import Depends,HTTPException,status,APIRouter
from App.Database.database import get_db
from sqlalchemy.orm import Session
from App.Routes.Auth_Users.login_register import get_current_user
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Cart.cart_model import Cart_Model,Cart_Item
from App.DataModels.Menu.menu_model import Pizza_Model
from typing import List
from App.Schemas.Cart.cart_schema import CartResponseSchema
#==========================Developing Router for Cart Menu=====================
cart_router=APIRouter()

#======================Customer	Get my cart with all items + total============
@cart_router.get("/get_your_cart",response_model=List[CartResponseSchema],status_code=status.HTTP_200_OK)
def get_cart(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #Fetcing Data From Data Base
    cart_item=db.query(Cart_Model).filter(Cart_Model.user_id==user.id).all()
    #Return Error
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You don't add any Item in Cart yet")
    #Return Result
    return cart_item

#====================Update Cart Item Quantity (Customer)=================================
@cart_router.put("/Update_cart_Item_quantity",status_code=status.HTTP_200_OK)
def Update_cart_Item_quantity(quantity:int,item_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
   #Fetcing Data From Data Base
    db_item=db.query(Cart_Model).filter(Cart_Model.id==item_id,Cart_Model.user_id==user.id).first()
    #Return Error
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Item not found in Cart Menu !")
    #Updating Quantity in database
    db_item.quantity=quantity
    db.commit()
    db.refresh(db_item)
    #Return Result
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
@cart_router.post("/add_item_to_cart/{item_id}",status_code=status.HTTP_200_OK)
def add_item_to_cart(item_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #Fetching Data From Data Base
    pizza=db.query(Pizza_Model).filter(Pizza_Model.id==item_id).first()
    #Return Error
    if not pizza:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Item is not present in database!")
    user_cart=db.query(Cart_Model).filter(Cart_Model.user_id==user.id).first()
    #Create Cart For User if not Present
    if not user_cart:
        user_cart = Cart_Model(user_id=user.id)
        db.add(user_cart)
        db.commit()
        db.refresh(user_cart) 
    #Query For Cart Item
    cart_item=db.query(Cart_Item).filter(Cart_Item.cart_id==user_cart.id,Cart_Item.pizza_id==item_id).first()
    if cart_item:
        cart_item.quantity+=1
    #If item not in Cart Table
    else:
        new_item = Cart_Item(
            cart_id=user_cart.id,
            pizza_id=item_id,
            quantity=1,
            size_id=1,
            unit_price=pizza.base_price,
            sub_total=pizza.base_price
        )

        db.add(new_item)
    db.commit()
    return {"Message":"Item has been Added to Cart Successfully!"}