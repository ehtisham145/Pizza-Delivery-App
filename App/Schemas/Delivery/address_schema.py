from pydantic import BaseModel,Field,validator
from typing import Optional
from App.Utils.constant import AddressStatusEnum
from enum import Enum
#=========================Address Create Schema========================
class AddressCreateSchema(BaseModel):
    label:AddressStatusEnum
    street:str=Field(...,min_length=3,max_length=50,example="Home")
    city:str=Field(...,min_length=3,max_length=50)
    zip_code: str = Field(..., pattern=r'^\d{5}$', description="5 digit zip code")
    is_default:bool=False
    class Config:
        from_attributes = True 
        json_schema_extra = {
            "example": {
                "label": "Home",
                "street": "123 Pizza Street, Sector G",
                "city": "Islamabad",
                "zip_code": "44000",
                "is_default": True
            }
        }
#=========================Address Response Schema========================
class AddressResponseSchema(BaseModel):
    label:AddressStatusEnum
    street:str=Field(...,min_length=3,max_length=50,example="Home")
    city:str=Field(...,min_length=3,max_length=50)
    zip_code: str = Field(..., pattern=r'^\d{5}$', description="5 digit zip code")
    model_config={
        "from_attributes":True
    }

#=========================Update Address Schema========================
class UpdateAddressSchema(BaseModel):
    label:AddressStatusEnum | None=None
    street:str| None=Field(...,min_length=3,max_length=50,example="Home")  
    city:str| None=Field(...,min_length=3,max_length=50) 
    zip_code:str| None = Field(..., pattern=r'^\d{5}$', description="5 digit zip code")
    is_default:bool | None=False
    model_config={
        "from_attributes":True
    }