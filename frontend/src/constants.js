// Mirrors backend/app/utils/constant.py

// The backend has no "list sizes" endpoint. These IDs match the order in
// which `python manage.py seed` inserts them (backend/app/database/seeds/data.py -> SIZES).
export const PIZZA_SIZES = [
  { id: 1, size: "Small", multiplier: 1.0 },
  { id: 2, size: "Medium", multiplier: 1.5 },
  { id: 3, size: "Large", multiplier: 2.0 },
  { id: 4, size: "X-large", multiplier: 2.5 },
];

export const PIZZA_CATEGORIES = [
  "Signature & Classics",
  "Meat Feast",
  "Garden Fresh",
  "Cheesy Indulgence",
  "Hot & Spicy",
  "Gourmet Fusion",
];

export const ORDER_STATUSES = ["Pending", "Delivered", "Cancelled"];
export const PAYMENT_STATUSES = ["Pending", "Paid", "Failed", "Refunded"];
export const PAYMENT_METHODS = ["Card", "Cash on Delivery"];
export const ADDRESS_LABELS = ["Home", "Office", "Other"];
export const ROLES = ["user", "staff", "admin"];
