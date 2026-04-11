from pydantic import BaseModel,Field,HttpUrl
from typing import Optional
from datetime import datetime
from App.DataModels.Menu_Model.menu_model import PizzaSize 
#=========================Category Validation===========================

class Category_Request(BaseModel): 
    name:str=Field(...,min_length=4,max_length=100)
    description:str
    model_config={
        #This actually allows pydantic to read data from sql data models 
        "form_attributes":True
    }

class Category_Response(Category_Request):
    id: int
    created_at: datetime
    model_config={
        "form_attributes":True
    }
#========================== Pizza Validation===========================


class Pizza_Request(BaseModel):
    name:str=Field(...,min_length=5,max_length=50)
    description:str=Field(...,max_length=500)
    base_price:float=Field(...,gt=0)    
    image_url:HttpUrl
    is_available:bool=True
    category_id:int

    model_config={
        "form_attributes":True
    }

class Pizza_Response(Pizza_Request):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config={
        "form_attributes":True
    }
#==========================Size Table===========================

class Size_Request(BaseModel):
    size:PizzaSize=Field(default=PizzaSize.MEDIUM)
    # price_multiplier must be a positive number
    # gt=0 ensures they can't set a 0 or negative price
    price_multiplier:float=Field(default=1.0,gt=0)

    model_config={
        "form_attributes":True
    }

class Size_Response(Size_Request):
    id:int
    created_at:datetime
    updated_at:datetime

    model_config={
        "form_attributes":True
    }
# 2. How to use it in your logic

# The goal of this table is to adjust the final price. In your backend logic, your calculation would look like this:

#     Total Price = Pizza.base_price×Size.price_multiplier

# Example Values:

#     Small: 0.8 (Discounted)

#     Medium: 1.0 (Base price)

#     Large: 1.5 (50% extra)

#     X-Large: 2.0 (Double price)

#==========================Topping Table===========================

class Topping_Request(BaseModel):    
    name:str=Field(...,min_length=5,max_length=100)
    extra_price:float=Field(gt=0)
    is_available:bool=True

    model_config={
        "form_attributes":True
    }