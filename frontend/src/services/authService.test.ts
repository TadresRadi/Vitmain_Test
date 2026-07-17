import { beforeEach, describe, expect, it, vi } from "vitest"

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock("@/lib/axios", () => ({
  default: apiMock,
  api: apiMock,
}))

describe("authService", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("logs in with email and password", async () => {
    const data = { access: "a", refresh: "r", user: { email: "user@test.dev" } }
    apiMock.post.mockResolvedValueOnce({ data })

    const { login } = await import("./authService")

    await expect(login("user@test.dev", "secret")).resolves.toBe(data)
    expect(apiMock.post).toHaveBeenCalledWith("/auth/login", {
      email: "user@test.dev",
      password: "secret",
    })
  })

  it("registers using the backend register endpoint", async () => {
    apiMock.post.mockResolvedValueOnce({ data: undefined })
    const payload = {
      email: "new@test.dev",
      password: "secret",
      password_confirm: "secret",
      full_name: "New User",
      phone_number: "01012345678",
      dob: "2000-01-01",
      user_type: "client",
    }

    const { register } = await import("./authService")

    await expect(register(payload)).resolves.toBeUndefined()
    expect(apiMock.post).toHaveBeenCalledWith("/auth/register", payload)
  })

  it("loads user and admin profiles from the expected endpoints", async () => {
    const { getProfile, getAdminProfile } = await import("./authService")
    apiMock.get
      .mockResolvedValueOnce({ data: { email: "user@test.dev" } })
      .mockResolvedValueOnce({ data: { email: "admin@test.dev" } })

    await expect(getProfile()).resolves.toEqual({ email: "user@test.dev" })
    await expect(getAdminProfile()).resolves.toEqual({ email: "admin@test.dev" })

    expect(apiMock.get).toHaveBeenNthCalledWith(1, "/users/profile")
    expect(apiMock.get).toHaveBeenNthCalledWith(2, "/admin/auth/profile")
  })

  it("posts admin login credentials to the admin endpoint", async () => {
    const data = { access_token: "admin-token" }
    apiMock.post.mockResolvedValueOnce({ data })

    const { adminLogin } = await import("./authService")

    await expect(adminLogin("admin@test.dev", "secret")).resolves.toBe(data)
    expect(apiMock.post).toHaveBeenCalledWith("/admin/auth/login", {
      email: "admin@test.dev",
      password: "secret",
    })
  })
})
