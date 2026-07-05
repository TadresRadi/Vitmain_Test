import { create } from "zustand";
import type { ApiError, LoginResponse } from "@/types/api";
import {
  getProfile,
  login as loginRequest,
  register as registerRequest,
} from "@/services/authService";

import { tokenStorage } from "@/lib/token-storage";
import { secureAxios } from "@/lib/secure-axios";

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
  auth_provider?: string;
  profile_picture?: string;
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

  logout: () => Promise<void>;

  fetchProfile: () => Promise<void>;

  setUser: (user: User) => void;

  setTokens: (
    accessToken: string,
    refreshToken: string,
    expiresIn?: number
  ) => void;

  clearError: () => void;

  changePassword: (
    oldPassword: string,
    newPassword: string
  ) => Promise<boolean>;

  resetPassword: (email: string) => Promise<boolean>;

  completePasswordReset: (
    email: string,
    token: string,
    newPassword: string
  ) => Promise<boolean>;

  loginWithGoogle: (idToken: string) => Promise<boolean>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: tokenStorage.isAuthenticated(),
  isLoading: false,
  error: null,
  onboarding_completed: null,

  setTokens: (accessToken, refreshToken, expiresIn) => {
    try {
      tokenStorage.setTokens(accessToken, refreshToken, expiresIn);

      set({
        isAuthenticated: true,
        error: null,
      });
    } catch {
      set({
        error: "Failed to save authentication",
      });
    }
  },

  setUser: (user) => {
    set({
      user,
      isAuthenticated: true,
      onboarding_completed: user.onboarding_completed ?? false,
    });
  },

  login: async (email, password) => {
    try {
      set({
        isLoading: true,
        error: null,
      });

      const data = await loginRequest(email, password);

      tokenStorage.setTokens(
        data.access_token,
        data.refresh_token
      );

      set({
        user: data.user,
        isAuthenticated: true,
        onboarding_completed: data.user.onboarding_completed,
        isLoading: false,
      });

      return data;
    } catch (err) {
      const error = err as ApiError;

      const message =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Login failed";

      set({
        error: message,
        isLoading: false,
      });

      throw error;
    }
  },

  register: async (
    email,
    password,
    password_confirm,
    full_name,
    phone_number,
    dob,
    user_type
  ) => {
    try {
      set({
        isLoading: true,
        error: null,
      });

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

      tokenStorage.setTokens(
        loginRes.access_token,
        loginRes.refresh_token
      );

      set({
        user: loginRes.user,
        isAuthenticated: true,
        onboarding_completed: loginRes.user.onboarding_completed,
        isLoading: false,
      });
    } catch (err) {
      const error = err as ApiError;

      const message =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Registration failed";

      set({
        error: message,
        isLoading: false,
      });

      throw error;
    }
  },

  logout: async () => {
    set({
      isLoading: true,
    });

    try {
      await secureAxios.getInstance().post("/api/auth/logout", {
        refresh_token: tokenStorage.getRefreshToken(),
      });
    } catch (error) {
      console.warn(error);
    } finally {
      tokenStorage.clear();

      set({
        user: null,
        isAuthenticated: false,
        onboarding_completed: null,
        error: null,
        isLoading: false,
      });
    }
  },

  fetchProfile: async () => {
    try {
      const profile = await getProfile();

      set({
        user: profile,
        onboarding_completed: profile.onboarding_completed ?? false,
      });
    } catch (err) {
      const error = err as ApiError;

      tokenStorage.clear();

      const message =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Failed to fetch profile";

      set({
        error: message,
        user: null,
        isAuthenticated: false,
        onboarding_completed: null,
      });
    }
  },

  changePassword: async (oldPassword, newPassword) => {
    try {
      set({
        isLoading: true,
        error: null,
      });

      await secureAxios.getInstance().post(
        "/api/auth/password/change",
        {
          old_password: oldPassword,
          new_password: newPassword,
          confirm_password: newPassword,
        }
      );

      set({
        isLoading: false,
      });

      return true;
    } catch (err: any) {
      set({
        isLoading: false,
        error:
          err.response?.data?.message ||
          "Failed to change password",
      });

      return false;
    }
  },

  resetPassword: async (email) => {
    try {
      set({
        isLoading: true,
        error: null,
      });

      await secureAxios
        .getInstance()
        .post("/api/auth/password/reset-request", {
          email,
        });

      set({
        isLoading: false,
      });

      return true;
    } catch (err: any) {
      set({
        isLoading: false,
        error:
          err.response?.data?.message ||
          "Failed to send reset email",
      });

      return false;
    }
  },

  completePasswordReset: async (
    email,
    token,
    newPassword
  ) => {
    try {
      set({
        isLoading: true,
        error: null,
      });

      await secureAxios.getInstance().post(
        "/api/auth/password/reset",
        {
          email,
          token,
          new_password: newPassword,
        }
      );

      set({
        isLoading: false,
      });

      return true;
    } catch (err: any) {
      set({
        isLoading: false,
        error:
          err.response?.data?.message ||
          "Failed to reset password",
      });

      return false;
    }
  },

  loginWithGoogle: async (idToken) => {
    try {
      set({
        isLoading: true,
        error: null,
      });

      const response = await secureAxios
        .getInstance()
        .post("/api/auth/google/callback", {
          id_token: idToken,
        });

      const {
        access_token,
        refresh_token,
        user,
      } = response.data;

      tokenStorage.setTokens(
        access_token,
        refresh_token
      );

      set({
        user,
        isAuthenticated: true,
        onboarding_completed: user.onboarding_completed,
        isLoading: false,
      });

      return true;
    } catch (err: any) {
      set({
        isLoading: false,
        error:
          err.response?.data?.message ||
          "Google login failed",
      });

      return false;
    }
  },

  clearError: () => {
    set({
      error: null,
    });
  },
}));