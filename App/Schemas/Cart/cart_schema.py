from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from App.Utils.constant import PizzaSizeEnum
from App.Schemas.Menu.menu_schema import Pizza_Request

# ======================== Supporting Info Schemas ========================
class ToppingInfo(BaseModel):
    """Lightweight topping info for cart display."""

    id:          int     = Field(..., description="Topping ID")
    name:        str     = Field(..., description="Topping name")
    extra_price: Decimal = Field(..., description="Extra charge for this topping")

    model_config = ConfigDict(from_attributes=True)


class SizeInfo(BaseModel):
    """Lightweight size info for cart display."""

    id:               int     = Field(..., description="Size ID")
    size:             str     = Field(..., description="Size name (e.g. Small, Medium, Large)")
    price_multiplier: Decimal = Field(..., description="Price multiplier for this size")

    model_config = ConfigDict(from_attributes=True)


# ======================== Add to Cart Schema ========================
class AddToCartSchema(BaseModel):
    """Schema for adding a pizza to the cart."""

    pizza_id:    int       = Field(..., gt=0,         description="ID of the pizza to add")
    size_id:     int       = Field(..., gt=0,         description="ID of the selected size")
    quantity:    int       = Field(1,  gt=0, le=10,   description="Quantity (max 10 per item)")
    topping_ids: int = Field(...,        description="Optional list of topping IDs")

    model_config = ConfigDict(from_attributes=True)


# ======================== Update Cart Item Schema ========================
class UpdateCartItemSchema(BaseModel):
    """Schema for updating the quantity of a cart item."""

    quantity: int = Field(..., gt=0, le=20, description="Updated quantity (max 20)")

    model_config = ConfigDict(from_attributes=True)


# ======================== Cart Item Response Schema ========================
class CartItemResponseSchema(BaseModel):
    """Schema for a single item in the cart response."""

    id:         int          = Field(..., description="Cart item ID")
    pizza_id:   int          = Field(..., description="ID of the pizza")
    quantity:   int          = Field(..., description="Quantity in cart")
    unit_price: Decimal      = Field(..., description="Price per unit")
    sub_total:  Decimal      = Field(..., description="Line total (unit_price × quantity)")
    size:       PizzaSizeEnum
    pizza:      PizzaInfo
    # toppings:   List[ToppingInfo] = []

    model_config = ConfigDict(from_attributes=True)


# ======================== Full Cart Response Schema ========================
class CartResponseSchema(BaseModel):
    """Schema for the full cart response."""

    id:          int                      = Field(..., description="Cart ID")
    items:       List[CartItemResponseSchema] = []
    total_price: Decimal                  = Field(..., description="Total price of all items")
    item_count:  int                      = Field(..., ge=0, description="Total number of items")

    model_config = ConfigDict(from_attributes=True)


# ======================== Lightweight Pizza Info for Cart ========================
class PizzaInfo(BaseModel):
    """Lightweight pizza info embedded in cart item responses."""

    id:          int     = Field(..., description="Pizza ID")
    name:        str     = Field(..., description="Pizza name")
    base_price:  Decimal = Field(..., description="Base price of the pizza")
    image_url:   str     = Field(..., description="Pizza image URL")

    model_config = ConfigDict(from_attributes=True)


CartItemResponseSchema.model_rebuild()  # Resolves the forward reference to PizzaInfo