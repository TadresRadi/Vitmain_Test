import api, { adminApi } from "@/lib/axios";
import type { LoginResponse, ProfileResponse } from "@/types/api";

export interface RegisterPayload {
  email: string;
  password: string;
  password_confirm: string;
  full_name: string;
  phone_number: string;
  dob: string;
  user_type: string;
}

export interface AdminLoginResponse {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    email: string;
    role: string;
    full_name?: string | null;
  };
}

export interface AdminProfileResponse {
  id: string;
  email: string;
  role: string;
  full_name?: string | null;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>("/auth/login", { email, password });
  return response.data;
}

export async function register(payload: RegisterPayload): Promise<void> {
  await api.post("/auth/register", payload);
}

export async function getProfile(): Promise<ProfileResponse> {
  const response = await api.get<ProfileResponse>("/users/profile");
  return response.data;
}

export async function adminLogin(email: string, password: string): Promise<AdminLoginResponse> {
  const response = await adminApi.post<AdminLoginResponse>("/admin/auth/login", { email, password });
  return response.data;
}

export async function getAdminProfile(): Promise<AdminProfileResponse> {
  const response = await adminApi.get<AdminProfileResponse>("/admin/auth/profile");
  return response.data;
}
