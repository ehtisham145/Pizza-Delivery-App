from sqlalchemy.orm import Session,joinedload
from fastapi import HTTPException,status,Depends,APIRouter
from sqlalchemy import func
from typing import List

from App.Utils.middleware import get_current_user,require_admin
from App.Database.database import get_db
from App.DataModels.Delivery.delivery_model import Delivery_Model
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Order.order_model import Order_Model
from App.Schemas.Delivery.address_schema import (
    AddressCreateSchema,
    AddressResponseSchema,
    UpdateAddressSchema
)
from App.Utils.db_helper import safe_commit

#===================Delivery Router======================
delivery_router=APIRouter()

#1.========================Customer Add new address==============================
@delivery_router.post(
    "/add_new_address/customer"
    ,status_code=status.HTTP_201_CREATED,
    response_model=AddressResponseSchema
)
def add_new_address(
    address:AddressCreateSchema
    ,db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
    #1.Check Address Length
    count_addresses=db.query(func.count(
        Delivery_Model.id)).filter(Delivery_Model.user_id==user.id).scalar()
   
    #2.Raise Error
    if count_addresses>=5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Maximum 5 Addresses are Allowed Per User !")

    if address.is_default:
        db.query(Delivery_Model).filter(
            Delivery_Model.user_id == user.id,
            Delivery_Model.is_default == True
        ).update({"is_default": False},synchronize_session=False)

    #3.Creating New Address   
    new_address=Delivery_Model(
            user_id=user.id,
            label=address.label,
            street=address.street,
            city=address.city,
            zip_code=address.zip_code,
            is_default=address.is_default
        )

    #4.Adding in Database
    db.add(new_address)
    safe_commit(db)
    db.refresh(new_address)
    return new_address


#2.========================Customer List All Addresses==============================
@delivery_router.get(
    "/get_all_addresses/customer",
    status_code=status.HTTP_200_OK,
    response_model=List[AddressResponseSchema]
)
def get_all_addresses(
    db:Session=Depends(get_db)
    ,user:User=Depends(get_current_user)
):
    all_addresses = (
        db.query(Delivery_Model)
        .filter(Delivery_Model.user_id == user.id)
        .all()
    )
    

    return all_addresses


#3.=================================Set One Address As Default Address=====================
@delivery_router.patch(
    "/set_default_address/customer/{address_id}"
    ,status_code=status.HTTP_200_OK,
    response_model=AddressResponseSchema
)
def set_deafult_address(
    address_id:int,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
    #1.Fetch User Address
    db_user_address=(db.query(Delivery_Model).filter(
        Delivery_Model.user_id==user.id,Delivery_Model.id==address_id
    ).first()
    )
    #2.Raise Error
    if not db_user_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Address Not Found !")
    
    #3.Setting All Default Addresses to False
    db.query(Delivery_Model).filter(
        Delivery_Model.user_id==user.id,
        Delivery_Model.is_default==True
    ).update({"is_default": False}, synchronize_session=False)

    #4.Updating User Address in DataBase
    db_user_address.is_default=True
    safe_commit(db)
    db.refresh(db_user_address)
    return db_user_address
    


#4.=================================Update Address Customer=====================

@delivery_router.patch(
    "/update_address/customer/{address_id}",
    status_code=status.HTTP_200_OK,
    response_model=AddressResponseSchema
)
def update_address(
    address_id:int,
    update_address:UpdateAddressSchema
    ,db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
    ):
    
    #1.Fetch User Address
    db_user_address=db.query(Delivery_Model).filter(
        Delivery_Model.user_id==user.id,Delivery_Model.id==address_id).first()
    
    #2.Raise Error
    if not db_user_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Address Not Found !")
    
    #3. Reset other defaults only if this address is being set as default ✅
    if update_address.is_default:
        db.query(Delivery_Model).filter(
            Delivery_Model.user_id == user.id,
            Delivery_Model.is_default == True
        ).update({"is_default": False},synchronize_session=False)

    #4.Updating User Address in DataBase
    # db_user_address.label=update_address.label
    # db_user_address.street=update_address.street
    # db_user_address.city=update_address.city
    # db_user_address.zip_code=update_address.zip_code
    # db_user_address.is_default=update_address.is_default
    for field, value in update_address.model_dump(exclude_unset=True).items():
        setattr(db_user_address, field, value)


    #5.Saving Changes in Database
    safe_commit(db)
    db.refresh(db_user_address)
    return db_user_address


#5.=================================================Deleting an Address Customer==================================

@delivery_router.delete(
    "/delete_Address/customer/{address_id}"
    ,status_code=status.HTTP_204_NO_CONTENT
)
def delete_address(
    address_id:int,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
    ):
   
    #1.Fetch User Address
    db_user_address=(db.query(Delivery_Model).filter(
        Delivery_Model.user_id==user.id,Delivery_Model.id==address_id).first()
    )
    #2.Raise Error
    if not db_user_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Address Not Found !")
    
    #3.Dont Delete Address if linked to an Order
    exists_order=db.query(Order_Model).filter(
        Order_Model.address_id==address_id).first()

    if exists_order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot delete address. It is linked to an existing order !")
    
    #4.Deleting Address
    db.delete(db_user_address)
    
    #5.Saving Changes in Database
    safe_commit(db)
    return {"Message":"Address Deleted Successfully !"}