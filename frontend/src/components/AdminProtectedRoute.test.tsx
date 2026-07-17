import { render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import AdminProtectedRoute from "./AdminProtectedRoute"

const mocks = vi.hoisted(() => ({
  useAdminAuthStore: vi.fn(),
}))

vi.mock("@/store/adminAuthStore", () => ({
  useAdminAuthStore: mocks.useAdminAuthStore,
}))

vi.mock("react-router-dom", () => ({
  Navigate: ({ to, replace }: { to: string; replace?: boolean }) => (
    <div data-replace={String(replace)} data-testid="navigate" data-to={to} />
  ),
}))

describe("AdminProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders children for authenticated admins", () => {
    mocks.useAdminAuthStore.mockReturnValue({ isAdminAuthenticated: true })

    render(
      <AdminProtectedRoute>
        <div>Admin content</div>
      </AdminProtectedRoute>
    )

    expect(screen.getByText("Admin content")).toBeInTheDocument()
  })

  it("redirects unauthenticated users to admin login", () => {
    mocks.useAdminAuthStore.mockReturnValue({ isAdminAuthenticated: false })

    render(
      <AdminProtectedRoute>
        <div>Admin content</div>
      </AdminProtectedRoute>
    )

    expect(screen.getByTestId("navigate")).toHaveAttribute("data-to", "/admin-login")
    expect(screen.getByTestId("navigate")).toHaveAttribute("data-replace", "true")
    expect(screen.queryByText("Admin content")).not.toBeInTheDocument()
  })
})
