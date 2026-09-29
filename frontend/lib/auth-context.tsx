"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { api, getToken, setToken } from "./api";
import type { MeResponse, Profile, User } from "./types";

interface AuthState {
  user: User | null;
  profile: Profile | null;
  loading: boolean; // initial session check in progress
}

interface AuthContextValue extends AuthState {
  refresh: () => Promise<void>;
  setUser: (user: User | null, profile: Profile | null) => void;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    profile: null,
    loading: true,
  });

  const refresh = useCallback(async () => {
    const token = getToken();
    if (!token) {
      setState({ user: null, profile: null, loading: false });
      return;
    }
    try {
      const me: MeResponse = await api.me();
      setState({ user: me.user, profile: me.profile, loading: false });
    } catch {
      setToken(null);
      setState({ user: null, profile: null, loading: false });
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const setUser = useCallback((user: User | null, profile: Profile | null) => {
    setState({ user, profile, loading: false });
  }, []);

  const signOut = useCallback(async () => {
    await api.logout();
    setState({ user: null, profile: null, loading: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, refresh, setUser, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
