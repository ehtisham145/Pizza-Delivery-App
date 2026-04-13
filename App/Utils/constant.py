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