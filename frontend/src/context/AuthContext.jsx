import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getSession, setSession } from "../api/client";
import { authApi, profileApi } from "../api/endpoints";

const AuthContext = createContext(null);

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

  const login = useCallback(async (email, password) => {
    const data = await authApi.login(email, password);
    // Save tokens first so the profile request is authenticated.
    setSession({ access_token: data.access_token, refresh: data.refresh_token, user: null });
    try {
      const user = await profileApi.get();
      setSession({ ...getSession(), user });
    } catch {
      setSession({ ...getSession(), user: { email: data.email, full_name: data.full_name, role: "user" } });
    }
  }, []);

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
