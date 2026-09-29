// Thin API client. All calls go through here so auth + error handling are
// consistent across screens. The browser app calls same-origin /api/* which
// Next.js proxies to the FastAPI backend (see next.config.js).

import type {
  AssessmentStatusResponse,
  AuthResponse,
  BusinessIdea,
  BusinessIdeaSummary,
  Dashboard,
  MeResponse,
  Profile,
} from "./types";

const TOKEN_KEY = "nashaa_token";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string,
    public fieldErrors?: { field: string; message: string }[],
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token === null) window.localStorage.removeItem(TOKEN_KEY);
  else window.localStorage.setItem(TOKEN_KEY, token);
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; auth?: boolean } = {},
): Promise<T> {
  const { method = "GET", body, auth = true } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      "Could not reach the server. Please check your connection and try again.",
      0,
    );
  }

  if (res.status === 204) return undefined as T;

  let payload: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!res.ok) {
    const data = payload as {
      detail?: string;
      errors?: { field: string; message: string }[];
    };
    const message =
      (data && typeof data === "object" && data.detail) ||
      "Something went wrong. Please try again.";
    throw new ApiError(
      typeof message === "string"
        ? message
        : "Please check the form and try again.",
      res.status,
      typeof message === "string" ? message : undefined,
      data?.errors,
    );
  }
  return payload as T;
}

// ---------- Auth ----------
export const api = {
  register(email: string, password: string, role: string, displayName: string) {
    return request<AuthResponse>("/api/auth/register", {
      method: "POST",
      auth: false,
      body: { email, password, role, display_name: displayName },
    });
  },
  login(email: string, password: string) {
    return request<AuthResponse>("/api/auth/login", {
      method: "POST",
      auth: false,
      body: { email, password },
    });
  },
  async logout() {
    try {
      await request("/api/auth/logout", { method: "POST" });
    } catch {
      // Even if the server call fails, clear the local token.
    }
    setToken(null);
  },
  me() {
    return request<MeResponse>("/api/auth/me");
  },
  requestPasswordReset(email: string) {
    return request<{ message: string; reset_token: string | null }>(
      "/api/auth/password-reset/request",
      { method: "POST", auth: false, body: { email } },
    );
  },
  confirmPasswordReset(token: string, newPassword: string) {
    return request<{ message: string }>("/api/auth/password-reset/confirm", {
      method: "POST",
      auth: false,
      body: { token, new_password: newPassword },
    });
  },

  // ---------- Profile ----------
  getProfile() {
    return request<Profile>("/api/profile");
  },
  updateProfile(patch: Partial<Profile>) {
    return request<Profile>("/api/profile", { method: "PUT", body: patch });
  },

  // ---------- Dashboard ----------
  dashboard() {
    return request<Dashboard>("/api/dashboard");
  },

  // ---------- Ideas ----------
  listIdeas() {
    return request<BusinessIdea[]>("/api/ideas");
  },
  getIdea(id: string) {
    return request<BusinessIdea | BusinessIdeaSummary>(`/api/ideas/${id}`);
  },
  createIdea(body: Partial<BusinessIdea>) {
    return request<BusinessIdea>("/api/ideas", { method: "POST", body });
  },
  updateIdea(id: string, body: Partial<BusinessIdea>) {
    return request<BusinessIdea>(`/api/ideas/${id}`, { method: "PUT", body });
  },
  setVisibility(id: string, visibility: string) {
    return request<BusinessIdea>(`/api/ideas/${id}/visibility`, {
      method: "PATCH",
      body: { visibility },
    });
  },
  deleteIdea(id: string) {
    return request<void>(`/api/ideas/${id}`, { method: "DELETE" });
  },

  // ---------- Assessments ----------
  getAssessmentStatus(id: string) {
    return request<AssessmentStatusResponse>(`/api/ideas/${id}/assessment`);
  },
  generateAssessment(id: string) {
    return request<AssessmentStatusResponse>(`/api/ideas/${id}/assessment`, {
      method: "POST",
    });
  },
};
