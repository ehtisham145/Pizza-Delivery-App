// Low-level HTTP client: token storage, JSON/form bodies, error parsing and
// a single automatic refresh-token retry on 401.

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");
const STORAGE_KEY = "pizza_auth";

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

// ── Session storage ─────────────────────────────────────────────
export function getSession() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || null;
  } catch {
    return null;
  }
}

export function setSession(session) {
  if (session) localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  else localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(new Event("auth:changed"));
}

// ── Error formatting (FastAPI returns `detail` as string or list) ─
function errorMessage(data, status) {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const field = Array.isArray(d.loc) ? d.loc.filter((l) => l !== "body").join(".") : "";
        return field ? `${field}: ${d.msg}` : d.msg;
      })
      .join(" · ");
  }
  if (status === 0) return "Could not reach the server. Is the backend running?";
  return `Request failed (${status})`;
}

function buildUrl(path, query) {
  const url = `${BASE_URL}${path}`;
  if (!query) return url;
  const params = new URLSearchParams();
  Object.entries(query).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") params.append(k, v);
  });
  const qs = params.toString();
  return qs ? `${url}?${qs}` : url;
}

// ── Refresh token flow ──────────────────────────────────────────
let refreshPromise = null;

async function refreshAccessToken() {
  const session = getSession();
  if (!session?.refresh) throw new ApiError("Session expired", 401);

  // The backend validates the full refresh-token object it returned at login.
  const res = await fetch(buildUrl("/auth/refresh-token"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(session.refresh),
  });
  if (!res.ok) throw new ApiError("Session expired", 401);
  const data = await res.json();

  setSession({
    ...session,
    access_token: data.access_token,
    refresh: { ...session.refresh, refresh_token: data.refresh_token },
  });
  return data.access_token;
}

// ── Main request helper ─────────────────────────────────────────
export async function request(path, { method = "GET", body, form, query, auth = true, retry = true } = {}) {
  const headers = {};
  let payload;

  if (form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    payload = new URLSearchParams(form).toString();
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  const session = getSession();
  if (auth && session?.access_token) headers.Authorization = `Bearer ${session.access_token}`;

  let res;
  try {
    res = await fetch(buildUrl(path, query), { method, headers, body: payload });
  } catch {
    throw new ApiError(errorMessage(null, 0), 0);
  }

  if (res.status === 401 && auth && retry && session?.refresh) {
    try {
      refreshPromise = refreshPromise || refreshAccessToken();
      await refreshPromise;
    } catch {
      setSession(null);
      throw new ApiError("Your session has expired. Please log in again.", 401);
    } finally {
      refreshPromise = null;
    }
    return request(path, { method, body, form, query, auth, retry: false });
  }

  if (res.status === 204) return null;

  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) throw new ApiError(errorMessage(data, res.status), res.status, data);
  return data;
}

// Many list endpoints answer 404 when nothing exists yet — treat as empty.
export async function listOrEmpty(promise) {
  try {
    const data = await promise;
    return Array.isArray(data) ? data : data ?? [];
  } catch (err) {
    if (err.status === 404) return [];
    throw err;
  }
}
