import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getSession, setSession } from "../api/client";
import { authApi, profileApi } from "../api/endpoints";

const AuthContext = createContext(null);

/** Where each role lands after login: admins and staff get the Admin Console. */
export function homeFor(role) {
  if (role === "admin") return "/admin";
  if (role === "staff") return "/admin/orders";
  return "/menu";
}

export function AuthProvider({ children }) {
  const [session, setSessionState] = useState(getSession);

  useEffect(() => {
    const sync = () => setSessionState(getSession());
    window.addEventListener("auth:changed", sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener("auth:changed", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  // Stores the tokens, then loads the full profile.
  const startSession = useCallback(async (data) => {
    // Save tokens first (quietly) so the profile request is authenticated; the
    // app only switches to "logged in" once the profile — and so the role — is
    // known. Otherwise an admin would briefly look like a customer.
    setSession({ access_token: data.access_token, refresh: data.refresh_token, user: null }, { notify: false });
    let user;
    try {
      user = await profileApi.get();
    } catch {
      user = { email: data.email, full_name: data.full_name, role: "user" };
    }
    setSession({ ...getSession(), user });
    return user;
  }, []);

  const login = useCallback(
    async (email, password) => {
      const data = await authApi.login(email, password);
      return startSession(data); // resolves to the user, so callers can route by role
    },
    [startSession]
  );


  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      /* token may already be invalid — clear locally anyway */
    }
    setSession(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    const user = await profileApi.get();
    setSession({ ...getSession(), user });
  }, []);

  const user = session?.user || null;
  const role = user?.role || "user";

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: Boolean(session?.access_token),
        isAdmin: role === "admin",
        isStaff: role === "admin" || role === "staff",
        home: homeFor(role),
        login,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
