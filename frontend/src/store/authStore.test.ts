import { beforeEach, describe, expect, it, vi } from "vitest"
import { useAuthStore } from "./authStore"
import { api } from "@/lib/axios"
import {
  getProfile,
  login as loginRequest,
  register as registerRequest,
} from "@/services/authService"
import { tokenStorage } from "@/lib/token-storage"

const mocks = vi.hoisted(() => ({
  apiPost: vi.fn(),
  clearTokens: vi.fn(),
  getProfile: vi.fn(),
  getRefreshToken: vi.fn(),
  isAuthenticated: vi.fn(),
  loginRequest: vi.fn(),
  registerRequest: vi.fn(),
  setTokens: vi.fn(),
}))

vi.mock("@/lib/axios", () => ({
  api: {
    post: mocks.apiPost,
  },
}))

vi.mock("@/services/authService", () => ({
  getProfile: mocks.getProfile,
  login: mocks.loginRequest,
  register: mocks.registerRequest,
}))

vi.mock("@/lib/token-storage", () => ({
  tokenStorage: {
    clear: mocks.clearTokens,
    getRefreshToken: mocks.getRefreshToken,
    isAuthenticated: mocks.isAuthenticated,
    setTokens: mocks.setTokens,
  },
}))

const user = {
  id: "user-1",
  email: "user@example.com",
  full_name: "User One",
  role: "user",
  onboarding_completed: true,
}

function resetStore() {
  useAuthStore.setState({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    onboarding_completed: null,
  })
}

describe("authStore", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    resetStore()
    mocks.getRefreshToken.mockReturnValue("refresh-token")
  })

  it("logs in, stores tokens, and updates authenticated state", async () => {
    mocks.loginRequest.mockResolvedValue({
      access_token: "access-token",
      refresh_token: "refresh-token",
      user,
    })

    const response = await useAuthStore.getState().login("user@example.com", "secret")

    expect(loginRequest).toHaveBeenCalledWith("user@example.com", "secret")
    expect(tokenStorage.setTokens).toHaveBeenCalledWith("access-token", "refresh-token")
    expect(response.user).toEqual(user)
    expect(useAuthStore.getState()).toMatchObject({
      user,
      isAuthenticated: true,
      isLoading: false,
      error: null,
      onboarding_completed: true,
    })
  })

  it("surfaces login API errors without authenticating", async () => {
    const error = { response: { data: { detail: "Invalid credentials" } } }
    mocks.loginRequest.mockRejectedValue(error)

    await expect(useAuthStore.getState().login("user@example.com", "bad")).rejects.toBe(error)

    expect(useAuthStore.getState()).toMatchObject({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: "Invalid credentials",
    })
  })

  it("registers then logs in the new user", async () => {
    mocks.registerRequest.mockResolvedValue(undefined)
    mocks.loginRequest.mockResolvedValue({
      access_token: "access-token",
      refresh_token: "refresh-token",
      user,
    })

    await useAuthStore
      .getState()
      .register("user@example.com", "secret", "secret", "User One", "01000000000", "2000-01-01", "owner")

    expect(registerRequest).toHaveBeenCalledWith({
      email: "user@example.com",
      password: "secret",
      password_confirm: "secret",
      full_name: "User One",
      phone_number: "01000000000",
      dob: "2000-01-01",
      user_type: "owner",
    })
    expect(tokenStorage.setTokens).toHaveBeenCalledWith("access-token", "refresh-token")
    expect(useAuthStore.getState().isAuthenticated).toBe(true)
  })

  it("logs out locally even when the API logout request fails", async () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => undefined)
    mocks.apiPost.mockRejectedValue(new Error("network"))
    useAuthStore.setState({
      user,
      isAuthenticated: true,
      onboarding_completed: true,
    })

    await useAuthStore.getState().logout()

    expect(api.post).toHaveBeenCalledWith("/auth/logout", { refresh_token: "refresh-token" })
    expect(tokenStorage.clear).toHaveBeenCalled()
    expect(useAuthStore.getState()).toMatchObject({
      user: null,
      isAuthenticated: false,
      onboarding_completed: null,
      error: null,
      isLoading: false,
    })
    warnSpy.mockRestore()
  })

  it("fetches a profile into the store", async () => {
    mocks.getProfile.mockResolvedValue(user)

    await useAuthStore.getState().fetchProfile()

    expect(getProfile).toHaveBeenCalled()
    expect(useAuthStore.getState()).toMatchObject({
      user,
      onboarding_completed: true,
    })
  })

  it("clears auth state when profile loading fails", async () => {
    mocks.getProfile.mockRejectedValue({ response: { data: { message: "Expired" } } })
    useAuthStore.setState({
      user,
      isAuthenticated: true,
      onboarding_completed: true,
    })

    await useAuthStore.getState().fetchProfile()

    expect(tokenStorage.clear).toHaveBeenCalled()
    expect(useAuthStore.getState()).toMatchObject({
      user: null,
      isAuthenticated: false,
      onboarding_completed: null,
      error: "Expired",
    })
  })

  it("uses the expected password and Google auth endpoints", async () => {
    mocks.apiPost
      .mockResolvedValueOnce({})
      .mockResolvedValueOnce({})
      .mockResolvedValueOnce({})
      .mockResolvedValueOnce({
        data: {
          access_token: "google-access",
          refresh_token: "google-refresh",
          user,
        },
      })

    await expect(useAuthStore.getState().changePassword("old", "new")).resolves.toBe(true)
    await expect(useAuthStore.getState().resetPassword("user@example.com")).resolves.toBe(true)
    await expect(
      useAuthStore.getState().completePasswordReset("user@example.com", "token", "new")
    ).resolves.toBe(true)
    await expect(useAuthStore.getState().loginWithGoogle("id-token")).resolves.toBe(true)

    expect(api.post).toHaveBeenNthCalledWith(1, "/auth/password/change", {
      old_password: "old",
      new_password: "new",
      confirm_password: "new",
    })
    expect(api.post).toHaveBeenNthCalledWith(2, "/auth/password/reset-request", {
      email: "user@example.com",
    })
    expect(api.post).toHaveBeenNthCalledWith(3, "/auth/password/reset", {
      email: "user@example.com",
      token: "token",
      new_password: "new",
    })
    expect(api.post).toHaveBeenNthCalledWith(4, "/auth/google/callback", {
      id_token: "id-token",
    })
    expect(tokenStorage.setTokens).toHaveBeenLastCalledWith("google-access", "google-refresh")
  })
})
