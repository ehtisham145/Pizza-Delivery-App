from enum import Enum
class PizzaCategoryEnum(str, Enum):
    SIGNATURE = "Signature & Classics"
    MEAT_FEAST = "Meat Feast"
    GARDEN_FRESH = "Garden Fresh"
    CHEESY = "Cheesy Indulgence"
    SPICY = "Hot & Spicy"
    FUSION = "Gourmet Fusion"

class PizzaSizeEnum(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE="x-large"


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