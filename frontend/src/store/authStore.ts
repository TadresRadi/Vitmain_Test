import { create } from "zustand";
import type { ApiError, LoginResponse } from "@/types/api";
import { getProfile, login as loginRequest, register as registerRequest } from "@/services/authService";

interface User {
  id: string;
  email: string;
  full_name: string | null;
  phone_number?: string | null;
  dob?: string | null;
  user_type?: string;
  role: string;
  is_active: boolean;
  language?: string;
  onboarding_completed?: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  onboarding_completed: boolean | null;
  login: (email: string, password: string) => Promise<LoginResponse>;
  register: (
    email: string,
    password: string,
    password_confirm: string,
    full_name: string,
    phone_number: string,
    dob: string,
    user_type: string
  ) => Promise<void>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem("token"),
  isLoading: false,
  error: null,
  onboarding_completed: null,

  login: async (email, password) => {
    try {
      set({ isLoading: true, error: null });
      const data = await loginRequest(email, password);
      localStorage.setItem("token", data.access_token);
      set({
        isAuthenticated: true,
        isLoading: false,
        onboarding_completed: data.user.onboarding_completed,
      });
      return data;
    } catch (err) {
      const error = err as ApiError;
      const message = error.response?.data?.detail || error.response?.data?.message || "Login failed";
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  register: async (email, password, password_confirm, full_name, phone_number, dob, user_type) => {
    try {
      set({ isLoading: true, error: null });
      await registerRequest({
        email,
        password,
        password_confirm,
        full_name,
        phone_number,
        dob,
        user_type,
      });

      const loginRes = await loginRequest(email, password);
      localStorage.setItem("token", loginRes.access_token);
      set({
        isAuthenticated: true,
        isLoading: false,
        onboarding_completed: loginRes.user.onboarding_completed,
      });
    } catch (err) {
      const error = err as ApiError;
      const message = error.response?.data?.detail || error.response?.data?.message || "Registration failed";
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem("token");
    set({ user: null, isAuthenticated: false, error: null, onboarding_completed: null });
  },

  fetchProfile: async () => {
    try {
      const profile = await getProfile();
      set({ user: profile });
    } catch (err) {
      const error = err as ApiError;
      const message = error.response?.data?.detail || error.response?.data?.message || "Failed to fetch profile";
      set({ error: message, user: null, isAuthenticated: false, onboarding_completed: null });
      localStorage.removeItem("token");
    }
  },
}));
