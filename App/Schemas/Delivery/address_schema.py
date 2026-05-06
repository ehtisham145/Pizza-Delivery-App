from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from App.Utils.constant import AddressStatusEnum


# ======================== Address Create Schema ========================
class AddressCreateSchema(BaseModel):
    """Schema for creating a new delivery address."""

    label:      AddressStatusEnum = Field(..., description="Address label (e.g. Home, Work)")
    street:     str               = Field(..., min_length=3, max_length=150,
                                          description="Street address",
                                          examples=["123 Pizza Street, Sector G"])
    city:       str               = Field(..., min_length=3, max_length=100,
                                          description="City name",
                                          examples=["Islamabad"])
    zip_code:   str               = Field(..., pattern=r'^\d{5}$',
                                          description="5-digit zip code",
                                          examples=["44000"])
    is_default: bool              = Field(False, description="Set as default address")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "label": "Home",
                "street": "123 Pizza Street, Sector G",
                "city": "Islamabad",
                "zip_code": "44000",
                "is_default": True
            }
        }
    )


# ======================== Address Response Schema ========================
class AddressResponseSchema(BaseModel):
    """Schema returned when fetching a delivery address."""

    id:         int               = Field(..., description="Address ID")
    label:      AddressStatusEnum = Field(..., description="Address label")
    street:     str               = Field(..., description="Street address")
    city:       str               = Field(..., description="City name")
    zip_code:   str               = Field(..., description="Zip code")
    is_default: bool              = Field(..., description="Whether this is the default address")
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ======================== Update Address Schema ========================
class UpdateAddressSchema(BaseModel):
    """Schema for partially updating a delivery address."""

    label:      Optional[AddressStatusEnum] = Field(None, description="Address label")
    street:     Optional[str]               = Field(None, min_length=3, max_length=150,
                                                    description="Street address")
    city:       Optional[str]               = Field(None, min_length=3, max_length=100,
                                                    description="City name")
    zip_code:   Optional[str]               = Field(None, pattern=r'^\d{5}$',
                                                    description="5-digit zip code")
    is_default: Optional[bool]              = Field(None, description="Set as default address")

    model_config = ConfigDict(from_attributes=True)