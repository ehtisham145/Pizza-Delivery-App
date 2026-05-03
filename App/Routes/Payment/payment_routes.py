from fastapi import Depends,HTTPException,APIRouter,status
from sqlalchemy.orm import Session
from App.Database.database import get_db
from App.Utils.middleware import get_current_user
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Order.order_model import Order_Model
from App.DataModels.Payment.payment_model import Payment_Model
from App.Schemas.Payment.payment_schemas import PaymentResponseSchema,PaymentStatusUpdateSchema,PaymentCreateSchema
from App.Utils.constant import PaymentStatusEnum
from typing import List
#Initialize Payment Router
payment_router=APIRouter()

#1.======================Get Payment History (Customer)=====================
@payment_router.get("/Get_Payment_History/Customer",status_code=status.HTTP_200_OK,response_model=List[PaymentResponseSchema])
def get_payment_history(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Fetching all Payment History
    all_payment_history=db.query(Payment_Model).filter(Payment_Model.user_id==user.id).all()
    #2.Raise Error if not found
    if not all_payment_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Payment History for this user not found !")
    
    return all_payment_history


#2=========================Create your Payment============================================================
@payment_router.post("/Create_Payment", status_code=status.HTTP_201_CREATED,response_model=PaymentResponseSchema)
def create_payment(payment_data: PaymentCreateSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
   
    #1.Fetch db Order    
    order = db.query(Order_Model).filter(
        Order_Model.id == payment_data.order_id,
        Order_Model.user_id == user.id
    ).first()

    #2.Raise Eror if not found
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    #3.Check If payment Already Exists
    existing_payment = db.query(Payment_Model).filter(
        Payment_Model.order_id == payment_data.order_id
    ).first()

   
    #4.Raise Error If Existing Payment
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment for this order already exists"
        )
    #5.Add Total price of order in amount
    new_payment = Payment_Model(
        order_id=payment_data.order_id,
        user_id=user.id,
        method=payment_data.method,
        amount=order.total_price,  
        status=PaymentStatusEnum.PENDING
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

#3.=======================Get Payment Details for Specific Order (order_id)===============================
@payment_router.get("/Get_Payment_detail/Customer/{order_id}",status_code=status.HTTP_200_OK,response_model=PaymentResponseSchema)
def get_payment_detail(order_id:str,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Fetch Detail from db
    order = db.query(Order_Model).filter(
        Order_Model.id == order_id,
        Order_Model.user_id == user.id
    ).first()
    #2.Raise Error If payment not found
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="This Order does not Exists in your Account")
    
    #3.Fetching Payment Detail
    payment_detail = db.query(Payment_Model).filter(
        Payment_Model.order_id == order_id,
        Payment_Model.user_id == user.id
    ).first()

    #4.Raise Error If payment not found
    if not payment_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Is order ki abhi tak koi payment nahi bani"  # ✅ Alag message
        )

    return payment_detail




#4.=============================Update payment status(Admin)===============================
@payment_router.patch("/Update_Payment_Status/Admin/{payment_id}",status_code=status.HTTP_200_OK,response_model=PaymentResponseSchema)
def update_payment_status(payment_id:str,new_status:PaymentStatusUpdateSchema,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Checking the Role
    if user.role!="admin":
           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can update payment status")
    #2.Fetching the payment from db
    db_payment=db.query(Payment_Model).filter(Payment_Model.id==payment_id).first()
    #3.Raise Error if not found
    if not db_payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Payment linked with this id is not found !")
    #4.Updating Status
    db_payment.status=new_status.status.value
    db.commit()
    db.refresh(db_payment)

    return db_payment



#5.=====================Get the List of all payments (Admin)============================
@payment_router.get("/Get_All_Payments/Admin",status_code=status.HTTP_200_OK,response_model=List[PaymentResponseSchema])
def get_all_payments(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Checking The Login Person Role
    if user.role!="admin":
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admin can see the all Payments Detail")
    #2.Fetching Data from Database
    all_payments=db.query(Payment_Model).all()
    #If no detail is found
    if not all_payments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Payment Found !")
    
    return all_payments 


