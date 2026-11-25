// Curated, verified Unsplash photos (free to use under the Unsplash License).
// Seeded pizzas store relative paths like "uploads/pizzas/x.jpg" that nothing
// serves, so we resolve a real photo by pizza name → category → rotation.

const unsplash = (id, w = 800) => `https://images.unsplash.com/photo-${id}?auto=format&fit=crop&w=${w}&q=80`;

const PHOTO = {
  cheesyTomato: "1513104890138-7c749659a591",
  chickenOnion: "1565299624946-b28f40a0ae38",
  margherita: "1574071318508-1cdbab80d002",
  chickenChunks: "1594007654729-407eedc4be65",
  pepperoni: "1628840042765-356cda07504e",
  sausage: "1604382354936-07c5d9983bd3",
  burrataGreens: "1593560708920-61dd98c46a4e",
  onionCheesePull: "1588315029754-2dd089d39a1a",
  spinachMushroom: "1555072956-7758afb20e8f",
  cheesePullDark: "1541745537411-b8046dc6d66c",
  basilMargherita: "1595854341625-f33ee10dbf94",
  tomatoPepper: "1576458088443-04a19bb13da6",
  pepperoniOlive: "1458642849426-cfb724f15ef7",
  slicePull: "1600028068383-ea11a7a101f3",
  woodFired: "1579751626657-72bc17010498",
  cheeseSlice: "1520201163981-8cc95007dd2a",
  pepperoniBoard: "1566843972142-a7fcb70de55a",
  veggieOlive: "1585238342024-78d387f4a707",
  pepperoniBox: "1534308983496-4fabb1a015ee",
  pepperoniSliceBox: "1601924582970-9238bcb495d9",
  darkBoard: "1613564834361-9436948817d1",
  fourCheese: "1620374645498-af6bd681a0bd",
  colourfulVeg: "1617470702892-e01504297e84",
  arugula: "1528137871618-79d2761e3fd5",
};

// Keyed by lower-cased pizza name (matches backend seeds).
const BY_NAME = {
  "chicken tikka": PHOTO.chickenChunks,
  "pepperoni passion": PHOTO.pepperoni,
  "veggie supreme": PHOTO.colourfulVeg,
  "fiery jalapeno": PHOTO.darkBoard,
  "beef delight": PHOTO.sausage,
  "fajita sensation": PHOTO.chickenOnion,
  "mushroom magic": PHOTO.spinachMushroom,
  "peri peri blast": PHOTO.pepperoniSliceBox,
  "cheese lover": PHOTO.fourCheese,
  "bbq chicken": PHOTO.onionCheesePull,
  margherita: PHOTO.margherita,
};

// Keyed by backend category name (PizzaCategoryEnum values).
const BY_CATEGORY = {
  "Signature & Classics": PHOTO.margherita,
  "Meat Feast": PHOTO.pepperoniOlive,
  "Garden Fresh": PHOTO.veggieOlive,
  "Cheesy Indulgence": PHOTO.cheeseSlice,
  "Hot & Spicy": PHOTO.tomatoPepper,
  "Gourmet Fusion": PHOTO.arugula,
};

const ROTATION = [
  PHOTO.cheesyTomato,
  PHOTO.basilMargherita,
  PHOTO.slicePull,
  PHOTO.pepperoniBoard,
  PHOTO.pepperoniBox,
  PHOTO.burrataGreens,
];

export const HERO_IMAGES = {
  login: unsplash(PHOTO.woodFired, 1600),
  register: unsplash(PHOTO.cheesePullDark, 1600),
  menuBanner: unsplash(PHOTO.burrataGreens, 1400),
  allCategory: unsplash(PHOTO.cheesyTomato, 200),
};

const isAbsolute = (url) => /^https?:\/\//i.test(String(url || ""));
const isUnsplash = (url) => /images\.unsplash\.com/.test(url);

function curatedId({ id, name, categoryName }) {
  const key = String(name || "").trim().toLowerCase();
  return BY_NAME[key] || BY_CATEGORY[categoryName] || ROTATION[Math.abs(Number(id) || key.length) % ROTATION.length];
}

/** Curated photo for a pizza (ignores its stored image_url). */
export function curatedPizzaImage(pizza, w = 800) {
  return unsplash(curatedId(pizza || {}), w);
}

/** Best image for a pizza: its own absolute URL if it has one, else curated. */
export function pizzaImage(pizza, w = 800) {
  if (pizza && isAbsolute(pizza.image_url)) return pizza.image_url;
  return curatedPizzaImage(pizza, w);
}

/** Responsive srcSet for Unsplash URLs (null for other hosts). */
export function srcSetFor(url) {
  if (!isUnsplash(url)) return undefined;
  return [400, 800, 1200].map((w) => `${url.replace(/([?&])w=\d+/, `$1w=${w}`)} ${w}w`).join(", ");
}

export function categoryImage(categoryName, w = 200) {
  return unsplash(BY_CATEGORY[categoryName] || PHOTO.cheesyTomato, w);
}
