from fastapi import Depends,HTTPException,APIRouter,status,Query
from typing import List
from sqlalchemy.orm import Session

from App.Database.database import get_db
from App.Utils.middleware import get_current_user,require_admin
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Order.order_model import Order_Model
from App.DataModels.Payment.payment_model import Payment_Model
from App.Schemas.Payment.payment_schemas import (
    PaymentResponseSchema,
    PaymentStatusUpdateSchema,
    PaymentCreateSchema
)
from App.Utils.constant import PaymentStatusEnum
from App.Utils.db_helper import safe_commit


#Initialize Payment Router
payment_router=APIRouter()
def _get_payment_or_404(payment_id: str, db: Session) -> Payment_Model:
    payment = db.query(Payment_Model).filter(Payment_Model.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id '{payment_id}' not found.",
        )
    return payment

#1.======================Get Payment History (Customer)=====================
@payment_router.get(
    "/get_payment_history/customer",
    status_code=status.HTTP_200_OK,
    response_model=List[PaymentResponseSchema]
)

def get_payment_history(
    skip:int=Query(default=0,ge=0,description="No of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Max records to return"),
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
    #1.Fetching all Payment History
    payment_history=db.query(Payment_Model).filter(
        Payment_Model.user_id==user.id
        ).order_by(Payment_Model.created_at.desc()).offset(skip).limit(limit).all()

    #2.Raise Error if not found
    if not payment_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="No Payment History Found For this Account !")
    
    return payment_history


#2=========================Create your Payment============================================================

@payment_router.post(
    "/create_payment",
     status_code=status.HTTP_201_CREATED,
     response_model=PaymentResponseSchema
)
def create_payment(
    payment_data: PaymentCreateSchema,
     db: Session = Depends(get_db),
      user: User = Depends(get_current_user)
):
   
    #1.Fetch db Order    
    order = (
        db.query(Order_Model).filter(
        Order_Model.id == payment_data.order_id,
        Order_Model.user_id == user.id
    ).first()
    )
    #2.Raise Eror if not found
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or does not belong to your accoun"
        )
    
    #3.Add Total price of order in amount
    new_payment = Payment_Model(
        order_id=payment_data.order_id,
        user_id=user.id,
        method=payment_data.method,
        amount=order.total_price,  
        status=PaymentStatusEnum.PENDING
    )

    try:
        db.add(new_payment)
        safe_commit(db)
        db.refresh(new_payment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A payment for this order already exists.",
        )

#3.=======================Get Payment Details for Specific Order (order_id)===============================

@payment_router.get(
    "/get_payment_detail/customer/{order_id}",
    status_code=status.HTTP_200_OK,
    response_model=PaymentResponseSchema
)

def get_payment_detail(
    order_id:str,
    db:Session=Depends(get_db),
    user:User=Depends(get_current_user)
):
   
    #1.Fetching Payment Detail
    payment_detail = db.query(Payment_Model).filter(
        Payment_Model.order_id == order_id,
        Payment_Model.user_id == user.id
    ).first()

    
    #2.Raise Error If payment not found
    if not payment_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payment found for this order in your account"
        )

    return payment_detail




#4.=============================Update payment status(Admin)===============================
@payment_router.patch(
    "/update_payment_status/admin/{payment_id}"
    ,status_code=status.HTTP_200_OK,
    response_model=PaymentResponseSchema
)
def update_payment_status(
    payment_id:str,
    new_status:PaymentStatusUpdateSchema,
    db:Session=Depends(get_db),
    user:User=Depends(require_admin)
):

    payment = _get_payment_or_404(payment_id, db)
    
    payment.status = new_status.status   # ← no .value needed
    db.commit()
    db.refresh(payment)
 
    return payment


#5.=====================Get the List of all payments (Admin)============================
@payment_router.get(
    "/get_all_payments/admin",
    status_code=status.HTTP_200_OK,
    response_model=List[PaymentResponseSchema]
)
def get_all_payments(
    skip: int = Query(default=0,ge=0),
    limit:int = Query(ge=0,default=10,ls=100),
    db:Session=Depends(get_db),
    user:User=Depends(require_admin)
):
    #1.Fetching Data from Database
    payments = (
        db.query(Payment_Model)
        .order_by(Payment_Model.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    #2.If no detail is found
    if not payments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Payment Found in System !")
    
    return payments 


