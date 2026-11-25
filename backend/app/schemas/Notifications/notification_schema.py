from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


# ======================== Notification Out Schema ========================
class NotificationOut(BaseModel):
    """Schema for a single notification."""

    id:         int      = Field(..., description="Notification ID")
    title:      str      = Field(..., description="Notification title")
    message:    str      = Field(..., description="Notification body")
    is_read:    bool     = Field(..., description="Whether the notification has been read")
    created_at: datetime = Field(..., description="When the notification was sent")

    model_config = ConfigDict(from_attributes=True)

# ======================== Notification List Schema ========================
class NotificationListOut(BaseModel):
    """Paginated list of notifications."""

    total:         int                  = Field(..., ge=0,        description="Total notification count")
    page:          int                  = Field(..., ge=1,        description="Current page number")
    size:          int                  = Field(..., ge=1, le=100, description="Items per page")
    notifications: List[NotificationOut] = Field(default=[], description="List of notifications")

    model_config = ConfigDict(from_attributes=True)


# ======================== Unread Count Schema ========================
class UnreadCountOut(BaseModel):
    """Schema for returning the unread notification count."""

    unread_count: int = Field(..., ge=0, description="Number of unread notifications")

    model_config = ConfigDict(from_attributes=True)