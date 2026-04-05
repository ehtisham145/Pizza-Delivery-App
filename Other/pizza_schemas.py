from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

# 1. Pizza Sizes (Str inheritance ensures JSON compatibility)
class PizzaSize(str, Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"

# 2. Pizza Categories 
class PizzaCategory(str, Enum):
    VEG = "Vegetarian"
    NON_VEG = "Non-Vegetarian"
    SPICY = "Spicy"
    PREMIUM = "Premium"
    DEAL = "Student Deal"

# 3. Pizza Create Schema Only For Admin 
class PizzaCreate(BaseModel):
    name: str=Field(min_length=3,max_length=100)
    price: int=Field(...,gt=0)
    description: str=Field(...,max_length=250)
    size: PizzaSize      
    category: PizzaCategory  
    is_available: bool = True
    model_config=ConfigDict(from_attributes=True)

#4. Show when Pizza is added
class PizzaResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str
    size: PizzaSize
    category: PizzaCategory
    is_available: bool
    
    model_config = ConfigDict(from_attributes=True)