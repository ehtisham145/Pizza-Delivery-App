from App.Database.database import Base, get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends, HTTPException, status, APIRouter, Query
from App.Utils.middleware import get_current_user, require_admin,get_user_or_404
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Order.order_model import Order_Model
from App.Schemas.Order.order_schemas import OrderResponseSchema
from App.Schemas.Auth_Users.User_Schema.register_schema import UserResponseSchema
from App.Utils.constant import OrderStatusEnum,RoleEnum
from App.Utils.db_helper import safe_commit
from datetime import date
from typing import List
from enum import Enum

admin_router = APIRouter()


# 1. Get Admin Stats ─────────────────────────────────────────────────────────

@admin_router.get("/get_stats_admin", status_code=status.HTTP_200_OK)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    today = date.today()

    # Merge today's aggregations into a single query
    today_stats = (
        db.query(
            func.count(Order_Model.id).label("orders"),
            func.coalesce(func.sum(Order_Model.total_price), 0).label("revenue"),
        )
        .filter(func.date(Order_Model.created_at) == today)
        .one()
    )

    # All-time stats
    all_time_stats = (
        db.query(
            func.count(Order_Model.id).label("orders"),
            func.coalesce(func.sum(Order_Model.total_price), 0).label("revenue"),
        )
        .one()
    )

    total_users = db.query(func.count(User.id)).scalar()
    total_pending = (
        db.query(func.count(Order_Model.id))
        .filter(Order_Model.status == "Pending")
        .scalar()
    )

    return {
        "total_orders_today": today_stats.orders,
        "total_revenue_today": today_stats.revenue,
        "total_orders_all_time": all_time_stats.orders,
        "total_revenue_all_time": all_time_stats.revenue,
        "total_users": total_users,
        "total_pending_orders": total_pending,
    }


# 2. Get All Users ────────────────────────────────────────────────────────────

@admin_router.get(
    "/get_all_user/admin",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponseSchema],
)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users = db.query(User).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found in the database.",
        )
    return users


# 3. Deactivate a User ────────────────────────────────────────────────────────

@admin_router.patch(
    "/deactivate_user/admin/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    # Guard: admin cannot deactivate themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account.",
        )

    target = get_user_or_404(user_id, db)

    if not target.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already inactive.",
        )

    target.is_active = False
    safe_commit(db)
    db.refresh(target)
    return target


# 4. Activate a User ──────────────────────────────────────────────────────────

@admin_router.patch(
    "/activate_user/admin/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    target = get_user_or_404(user_id, db)

    if target.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active.",
        )

    target.is_active = True
    safe_commit(db)
    db.refresh(target)
    return target


# 5. Change User Role ─────────────────────────────────────────────────────────
ALLOWED_ROLES = {role.value for role in RoleEnum}   # {"admin", "user", "staff"}

@admin_router.patch(
    "/change_role/admin/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponseSchema,
)
def change_role(
    user_id: int,
    assign_role: RoleEnum = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    # 1. Fetch target user
    target = get_user_or_404(user_id, db)

    #2. Resolve to string value first — single source of truth
    new_role = assign_role.value

    # 3. Defense-in-depth: validate BEFORE touching the object
    if new_role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{new_role}'. Allowed: {sorted(ALLOWED_ROLES)}",
        )

    # 4. Business rules
    if target.role == RoleEnum.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change the role of another admin.",
        )

    if target.role == new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already has the '{new_role}' role.",
        )

    # 5. Mutate only after all checks pass
    target.role = new_role
    safe_commit(db)
    db.refresh(target)
    return target

# 6. Get All Orders with Filter ───────────────────────────────────────────────

@admin_router.get(
    "/get_all_orders/admin/{order_status}",
    status_code=status.HTTP_200_OK,
    response_model=List[OrderResponseSchema],
)
def get_all_orders(
    order_status: OrderStatusEnum,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    orders = (
        db.query(Order_Model)
        .filter(Order_Model.status == order_status.value)
        .all()
    )
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No '{order_status.value}' orders found.",
        )
    return orders