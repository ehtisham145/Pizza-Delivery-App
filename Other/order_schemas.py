from pydantic import BaseModel,Field,field_validator
from typing import Literal,Optional

#-------------------------Order Request---------------------------------------
# 2. Order ke liye Schemas (Request/Input)
class OrderModel(BaseModel):
    quantity: int = Field(..., gt=0) # Quantity 0 se bari honi chahiye
    order_status: Literal["PENDING", "IN-TRANSIT", "DELIVERED"] = "PENDING"
    pizza_sizes: Literal["SMALL", "MEDIUM", "LARGE", "EXTRA-LARGE"] = "SMALL"
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

# Bilkul. Agar from_attributes = True set ho, to Pydantic direct Python objects ke attributes
# se data read kar lega aur error throw nahi karega.


#-------------------------Order Response---------------------------------------
# 3. Order ke liye Schema (Response/Output) 
# Ye wo hai jo user ko nazar aayega (GET request par)
#just to show user name
class UserSnippet(BaseModel):
    username:str
    class Config:
        from_attributes = True
class OrderResponseModel(BaseModel):
    id: int
    quantity: int
    order_status: str
    pizza_sizes: str
    # Is line ko Optional kar dein
    user: Optional[UserSnippet] = None

    # ChoiceType handling: Ye Validator Choice object se string nikal lega
    @field_validator("order_status", "pizza_sizes", mode="before")
    @classmethod
    def convert_choice_to_str(cls, v):
        # Agar SQLAlchemy ChoiceType object hai toh uski value uthao
        if hasattr(v, "value"):
            return v.value
        return v

    class Config:
        from_attributes = True