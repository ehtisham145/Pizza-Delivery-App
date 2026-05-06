from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from App.Utils.constant import PizzaSizeEnum, PizzaCategoryEnum


# ======================== Category Schemas ========================
class Category_Request(BaseModel):
    """Schema for creating or updating a category."""

    name:        PizzaCategoryEnum   = Field(..., description="Category type")
    description: Optional[str]       = Field(None, max_length=500, description="Category description")

    model_config = ConfigDict(from_attributes=True)


class Category_Response(BaseModel):
    """Schema returned when fetching a category."""

    id:          int              = Field(..., description="Category ID")
    name:        PizzaCategoryEnum = Field(..., description="Category type")
    description: Optional[str]    = Field(None, description="Category description")
    created_at:  datetime
    updated_at:  Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ======================== Pizza Schemas ========================
class Pizza_Request(BaseModel):
    """Schema for creating or updating a pizza."""

    name:        str     = Field(..., min_length=5, max_length=50,  description="Pizza name")
    description: str     = Field(..., max_length=500,               description="Pizza description")
    base_price:  Decimal = Field(..., gt=0, decimal_places=2,       description="Base price before size multiplier")
    image_url:   HttpUrl = Field(...,                               description="URL of pizza image")
    is_available: bool   = Field(True,                              description="Whether pizza is orderable")
    category_id: int     = Field(...,                               description="ID of the pizza category")

    model_config = ConfigDict(from_attributes=True)


class Pizza_Response(BaseModel):
    """Schema returned when fetching a pizza."""

    id:           int     = Field(..., description="Pizza ID")
    name:         str     = Field(..., description="Pizza name")
    description:  str     = Field(..., description="Pizza description")
    base_price:   Decimal = Field(..., description="Base price")
    image_url:    str     = Field(..., description="Pizza image URL")
    is_available: bool    = Field(..., description="Whether pizza is orderable")
    category_id:  int     = Field(..., description="Category ID")
    created_at:   datetime
    updated_at:   Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ======================== Size Schemas ========================
class Size_Request(BaseModel):
    """Schema for creating or updating a size."""

    size:             PizzaSizeEnum = Field(..., description="Pizza size")
    price_multiplier: Decimal       = Field(default=Decimal("1.0"), gt=0,
                                            decimal_places=2,
                                            description="Price multiplier applied to base price")

    model_config = ConfigDict(from_attributes=True)


class Size_Response(BaseModel):
    """Schema returned when fetching a size."""

    id:               int           = Field(..., description="Size ID")
    size:             PizzaSizeEnum = Field(..., description="Pizza size")
    price_multiplier: Decimal       = Field(..., description="Price multiplier")
    created_at:       datetime
    updated_at:       Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ======================== Topping Schemas ========================
class Topping_Request(BaseModel):
    """Schema for creating or updating a topping."""

    name:         str     = Field(..., min_length=2, max_length=100, description="Topping name")
    extra_price:  Decimal = Field(..., gt=0, decimal_places=2,       description="Extra charge for this topping")
    is_available: bool    = Field(True,                              description="Whether topping is currently available")

    model_config = ConfigDict(from_attributes=True)


class Topping_Response(BaseModel):
    """Schema returned when fetching a topping."""

    id:           int     = Field(..., description="Topping ID")
    name:         str     = Field(..., description="Topping name")
    extra_price:  Decimal = Field(..., description="Extra charge")
    is_available: bool    = Field(..., description="Availability status")
    created_at:   datetime
    updated_at:   Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)