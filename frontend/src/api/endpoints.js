// One function per backend route. Paths match the FastAPI routers in
// backend/main.py exactly (the /api prefix is added by the client and
// stripped again by nginx / the Vite proxy).
import { request, listOrEmpty } from "./client";

// ── Authentication ──────────────────────────────────────────────
export const authApi = {
  register: (data) => request("/auth/register", { method: "POST", body: { ...data, role: "customer" }, auth: false }),
  login: (email, password) =>
    request("/auth/login", { method: "POST", form: { username: email, password }, auth: false }),
  logout: () => request("/auth/logout", { method: "POST" }),
};

// ── Profile ─────────────────────────────────────────────────────
export const profileApi = {
  get: () => request("/profile/get-user-profile"),
  update: (data) => request("/profile/update-profile", { method: "PUT", body: data }),
  changePassword: (data) => request("/profile/change-password", { method: "PUT", body: data }),
};

// ── Menu: pizzas, categories, toppings ─────────────────────────
export const menuApi = {
  pizzas: () => listOrEmpty(request("/menu/get_all_pizzas")),
  pizza: (id) => request(`/menu/pizza_by_id/${id}`),
  createPizza: (data) => request("/menu/create_pizza", { method: "POST", body: data }),
  updatePizza: (id, data) => request(`/menu/update_pizza/${id}`, { method: "PUT", body: data }),
  setPizzaAvailability: (id, is_available) =>
    request(`/menu/update_pizza_status/${id}`, { method: "PATCH", body: { is_available } }),
  deletePizza: (id) => request(`/menu/pizzas/${id}`, { method: "DELETE" }),

  categories: () => listOrEmpty(request("/menu/view_categories")),
  createCategory: (name, description) =>
    request("/menu/create_category", { method: "POST", body: { name, description } }),

  toppings: () => listOrEmpty(request("/menu/all_toppings")),
  createTopping: (data) => request("/menu/create_toppings", { method: "POST", body: data }),
  updateTopping: (id, data) => request(`/menu/update_topping/${id}`, { method: "PUT", body: data }),
};

// ── Cart ────────────────────────────────────────────────────────
export const cartApi = {
  get: () => listOrEmpty(request("/cart/get_your_cart")),
  add: (pizzaId, { size_id, quantity, topping_ids = 0 }) =>
    request(`/cart/add_item_to_cart/${pizzaId}`, {
      method: "POST",
      body: { pizza_id: pizzaId, size_id, quantity, topping_ids },
    }),
  updateQuantity: (itemId, quantity) =>
    request("/cart/update_cart_Item_quantity", { method: "PATCH", query: { item_id: itemId, quantity } }),
  removeItem: (itemId) => request(`/cart/delete_cart_item/${itemId}`, { method: "DELETE" }),
  clear: () => request("/cart/delete_entire_cart", { method: "DELETE" }),
};

// ── Delivery addresses ──────────────────────────────────────────
export const addressApi = {
  list: () => listOrEmpty(request("/delivery/get_all_addresses/customer")),
  add: (data) => request("/delivery/add_new_address/customer", { method: "POST", body: data }),
  update: (id, data) => request(`/delivery/update_address/customer/${id}`, { method: "PATCH", body: data }),
  setDefault: (id) => request(`/delivery/set_default_address/customer/${id}`, { method: "PATCH" }),
  remove: (id) => request(`/delivery/delete_Address/customer/${id}`, { method: "DELETE" }),
};

// ── Orders ──────────────────────────────────────────────────────
export const orderApi = {
  placeFromCart: (address_id, notes) =>
    request("/order/place_order_from_cart/user", { method: "POST", body: { address_id, notes: notes || null } }),
  history: () => request("/order/get_orders_history/user"),
  mine: (id) => request(`/order/get_order_by_id/user/${id}`),
  cancel: (id) => request(`/order/cancel_Order/User/${id}`, { method: "PATCH" }),

  // admin / staff
  all: ({ page = 1, page_size = 20, order_status } = {}) =>
    listOrEmpty(request("/order/get_all_orders/admin", { query: { page, page_size, order_status } })),
  adminGet: (id) => request(`/order/admin/get_orders/${id}`),
  updateStatus: (id, new_status) =>
    request(`/order/update_order_status/admin/${id}`, { method: "PATCH", body: { new_status } }),
};

// ── Payments ────────────────────────────────────────────────────
export const paymentApi = {
  history: ({ skip = 0, limit = 50 } = {}) =>
    listOrEmpty(request("/payment/get_payment_history/customer", { query: { skip, limit } })),
  create: (order_id, method) => request("/payment/create_payment", { method: "POST", body: { order_id, method } }),
  forOrder: (orderId) => request(`/payment/get_payment_detail/customer/${orderId}`),

  // admin
  all: ({ skip = 0, limit = 50 } = {}) =>
    listOrEmpty(request("/payment/get_all_payments/admin", { query: { skip, limit } })),
  updateStatus: (id, status) =>
    request(`/payment/update_payment_status/admin/${id}`, { method: "PATCH", body: { status } }),
};

// ── Reviews ─────────────────────────────────────────────────────
export const reviewApi = {
  submit: (data) => request("/review/submit_review", { method: "POST", body: data }),
  mine: ({ skip = 0, limit = 50 } = {}) => listOrEmpty(request("/review/history", { query: { skip, limit } })),
  forPizza: (pizzaId, { skip = 0, limit = 20 } = {}) =>
    listOrEmpty(request(`/review/reviews/pizza/${pizzaId}`, { query: { skip, limit }, auth: false })),

  // admin / staff
  all: ({ skip = 0, limit = 50 } = {}) => listOrEmpty(request("/review/reviews", { query: { skip, limit } })),
  remove: (id) => request(`/review/reviews/${id}`, { method: "DELETE" }),
};

// ── Notifications ───────────────────────────────────────────────
export const notificationApi = {
  list: ({ page = 1, size = 20 } = {}) => request("/notifications/get_notifications", { query: { page, size } }),
  markRead: (id) => request(`/notifications/mark_as_read_notification/${id}`, { method: "PATCH" }),
  markAllRead: () => request("/notifications/mark_all_notification_as_read", { method: "PATCH" }),
  unreadCount: async () => {
    const data = await request("/notifications/unread/notifications/count");
    return data?.unread_count ?? data?.count ?? 0;
  },
};

// ── Admin ───────────────────────────────────────────────────────
export const adminApi = {
  stats: () => request("/admin/get_stats_admin"),
  users: () => listOrEmpty(request("/admin/get_all_user/admin")),
  activate: (id) => request(`/admin/activate_user/admin/${id}`, { method: "PATCH" }),
  deactivate: (id) => request(`/admin/deactivate_user/admin/${id}`, { method: "PATCH" }),
  changeRole: (id, role) => request(`/admin/change_role/admin/${id}`, { method: "PATCH", query: { assign_role: role } }),
  ordersByStatus: (status) => listOrEmpty(request(`/admin/get_all_orders/admin/${encodeURIComponent(status)}`)),
};
