from app.database.database import get_db
from fastapi import Depends,APIRouter,HTTPException,status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import Query

from app.utils.middleware import get_current_user,require_admin,require_admin_or_staff
from app.datamodels.Reviews.reviews_model import Review_Model
from app.datamodels.Auth_Users.user_model import User
from app.datamodels.Order.order_model import Order_Model, Order_Item_Model
from app.utils.constant import OrderStatusEnum
from app.utils.db_helper import safe_commit
from app.schemas.Reviews.review_schemas import (
    ReviewCreateSchema,ReviewResponseSchema
)
from typing import List

#Create Review Router
review_router=APIRouter()

# ─────────────────────────────────────────────
# Helper: reusable review fetcher
# ─────────────────────────────────────────────

def _get_review_or_404(review_id: int, db: Session) -> Review_Model:
    review = db.query(Review_Model).filter(Review_Model.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with id '{review_id}' not found.",
        )
    return review

#1.=====================Submit a Review (User)===============================
@review_router.post(
    "/submit_review",
     status_code=status.HTTP_201_CREATED,
      response_model=ReviewResponseSchema
)
def submit_a_review(
    rev: ReviewCreateSchema, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    
    # 1. Order must exist AND belong to the current user (prevents reviewing other people's orders)
    order = (db.query(Order_Model).filter(
        Order_Model.id == rev.order_id,
        Order_Model.user_id == user.id,
    ).first())

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found or does not belong to your account!")

    # 2. Only delivered orders can be reviewed
    if order.status != OrderStatusEnum.DELIVERED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="You can only review an order after it has been delivered.")

    # 3. The reviewed pizza must be part of that order
    in_order = db.query(Order_Item_Model).filter(
        Order_Item_Model.order_id == order.id,
        Order_Item_Model.pizza_id == rev.pizza_id,
    ).first()
    if not in_order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="This pizza is not part of the selected order.")

    # 4. One review per order (also enforced by the unique constraint below)
    if db.query(Review_Model).filter(Review_Model.order_id == order.id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
        detail="You have already submitted a review for this order.")

    # 5. Create and save review
    new_review = Review_Model(
        order_id=rev.order_id,
        pizza_id=rev.pizza_id,
        rating=rev.rating,
        comment=rev.comment,
        user_id=user.id
    )
    try:
        db.add(new_review)
        safe_commit(db)
        db.refresh(new_review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already submitted a review for this order.",
        )
 
    return new_review



#2.=====================(Review History)/Customer===============================
@review_router.get(
    "/history",
    status_code=status.HTTP_200_OK
    ,response_model=List[ReviewResponseSchema]
)
def get_reviews_history(
    db:Session=Depends(get_db),
    skip : int = Query(ge=0,default=0),
    limit : int = Query(ge=1,default=10,le=100),
    user:User=Depends(get_current_user)
):
    #1.Fetching Reviews from Database
    reviews=(db.query(Review_Model).filter(
        Review_Model.user_id==user.id).order_by(Review_Model.created_at.desc()).offset(skip).limit(limit).all()
    )

    #2.Raise Error If no Reviews Found
    if not reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Reviews has been found your Account !")

    return reviews



#3.=====================Get All Reviews (Admin)===============================
@review_router.get(
    "/reviews"
    ,status_code=status.HTTP_200_OK
    ,response_model=List[ReviewResponseSchema]
)
def get_all_reviews(
    db:Session=Depends(get_db),
    skip: int =Query(default=0,ge=0),
    limit: int =Query(default=10,ge=1,le=100),
    user:User=Depends(require_admin)
):
    #1.Fetch every review in the system (not just the admin's own)
    reviews=(db.query(Review_Model)
    .order_by(Review_Model.created_at.desc()).offset(skip).limit(limit).all())
    
    #2.Raise Error if Reviews not found
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found in the system.",
        )

    #3.Return Output
    return reviews

#4.=====================Delete a Review (Admin)===============================
@review_router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_200_OK
)
def delete_a_review(
    review_id:int,
    db:Session=Depends(get_db)
    ,user:User=Depends(require_admin_or_staff)
):
    review = _get_review_or_404(review_id, db)
 
    db.delete(review)
    safe_commit(db)
 
    return {"message": "Review deleted successfully."}

#5.=====================Public Reviews for a pizza (pizza_id)========================
@review_router.get(
    "/reviews/pizza/{pizza_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ReviewResponseSchema]
)
def get_review_for_pizza(
    pizza_id:int,
    skip : int = Query (default=0,ge=0),
    limit : int = Query (default=10,ge=1,le=100),
    db:Session=Depends(get_db)
): 
    #1.Fetching Review from DB
    pizza_review=db.query(Review_Model).filter(
        Review_Model.pizza_id==pizza_id
        ).order_by(Review_Model.created_at.desc()).offset(skip).limit(limit).all()

    #2.Raise Error If Review not Found
    if not pizza_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review Not Found for this Pizza !")

    return pizza_review