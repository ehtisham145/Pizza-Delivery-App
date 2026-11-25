from enum import Enum
from sqlalchemy.types import TypeDecorator, String
import uuid
class PizzaCategoryEnum(str, Enum):
    SIGNATURE = "Signature & Classics"
    MEAT_FEAST = "Meat Feast"
    GARDEN_FRESH = "Garden Fresh"
    CHEESY = "Cheesy Indulgence"
    SPICY = "Hot & Spicy"
    FUSION = "Gourmet Fusion"

class PizzaSizeEnum(str, Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    EXTRA_LARGE="X-large"


class PizzaToppingEnum(str, Enum):
    EXTRA_CHEESE = "Extra Cheese"
    PEPPERONI = "Pepperoni"
    MUSHROOMS = "Mushrooms"
    ONIONS = "Onions"
    OLIVES = "Olives"
    GREEN_PEPPERS = "Green Peppers"
    CHICKEN_TIKKA = "Chicken Tikka"
    JALAPENOS = "Jalapenos"
    BEEF_PEPPERONI = "Beef Pepperoni"
    

class OrderStatusEnum(str, Enum):
    PENDING = "Pending"        
    DELIVERED = "Delivered"      
    CANCELLED = "Cancelled"   

class AddressStatusEnum(str,Enum):
    HOME="Home"
    OFFICE="Office"
    OTHER="Other"

class PaymentStatusEnum(str,Enum):
    PENDING="Pending"
    PAID="Paid"
    FAILED="Failed"
    REFUNDED="Refunded"

class PaymentMethodEnum(str,Enum):
    CARD="Card"
    CASH_ON_DELIVERY="Cash on Delivery"


# --- Enums & Helpers ---

class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"
    staff = "staff"  # extend as needed