from App.Database.database import get_db
from fastapi import Depends,APIRouter,HTTPException,status
from sqlalchemy.orm import Session
from App.Utils.middleware import get_current_user,require_admin
from App.DataModels.Reviews.reviews_model import Review_Model
from App.DataModels.Order.order_model import Order_Model
from App.Schemas.Reviews.review_schemas import ReviewCreateSchema,ReviewResponseSchema
from typing import List

#Create Review Router
review_router=APIRouter()

#1.=====================Submit a Review (User)===============================
@review_router.post("/submit_review", status_code=status.HTTP_201_CREATED, response_model=ReviewResponseSchema)
def submit_a_review(rev: ReviewCreateSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    
    # 1. Check if order exists
    valid_order = db.query(Order_Model).filter(Order_Model.id == rev.order_id).first()
    if not valid_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found!")

    # 2. Check if order belongs to current user
    if valid_order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This order does not belong to you!")

    # 3. Check if review already exists for this order
    existing_review = db.query(Review_Model).filter(Review_Model.order_id == rev.order_id).first()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review already exists for this order!")

    # 4. Create and save review
    new_review = Review_Model(
        order_id=rev.order_id,
        rating=rev.rating,
        comment=rev.comment,
        user_id=user.id
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


#2.=====================(Review History)/Customer===============================
@review_router.get("/history",status_code=status.HTTP_200_OK,response_model=List[ReviewResponseSchema])
def get_reviews_history(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    #1.Fetching Reviews from Database
    review_history=db.query(Review_Model).filter(Review_Model.user_id==user.id).all()
    return review_history



#3.=====================Get All Reviews (Admin)===============================
@review_router.get("/reviews",status_code=status.HTTP_200_OK,response_model=List[ReviewResponseSchema])
def get_all_reviews(db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.Fetch Reviews from DB
    all_reviews=db.query(Review_Model).all()
    #2.Return Output
    return all_reviews

#4.=====================Delete a Review (Admin)===============================
@review_router.get("/reviews/{review_id}",status_code=status.HTTP_200_OK)
def delete_a_review(review_id:int,db:Session=Depends(get_db),user:User=Depends(require_admin)):
    #1.Fetch Review from DB
    review_to_delete=db.query(Review_Model).filter(Review_Model.id==review_id).first()
    #2.Raise Error if no Review is found
    if not review_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review not found !")
    #3.Delete Review
    db.delete(review_to_delete)
    db.commit()
    #4.Return Output
    return {"Message":"Review Deleted Successfully !"}

#5.=====================Public Reviews for a pizza (pizza_id)========================
@review_router.get("/reviews/pizza/{pizza_id}",status_code=status.HTTP_200_OK,response_model=List[ReviewResponseSchema])
def get_review_for_pizza(pizza_id:int,db:Session=Depends(get_db)): 
    #1.Fetching Review from DB
    pizza_review=db.query(Review_Model).filter(Review_Model.pizza_id==pizza_id).all()
    #2.Raise Error If Review not Found
    if not pizza_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review Not Found !")
    return pizza_review