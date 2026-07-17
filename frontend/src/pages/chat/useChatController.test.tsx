import { act, renderHook, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import type { AIPostGeneration } from "@/types/api"

const navigateMock = vi.hoisted(() => vi.fn())
const toastMock = vi.hoisted(() => vi.fn())
const locationState = vi.hoisted(() => ({ current: undefined as unknown }))
const chatServiceMock = vi.hoisted(() => ({
  completePostReview: vi.fn(),
  generateImages: vi.fn(),
  generatePremiumPosts: vi.fn(),
  getImagesHistory: vi.fn(),
  getPremiumPosts: vi.fn(),
  mapLatestSessionImages: vi.fn(),
  regenerateSelectedPosts: vi.fn(),
  shouldReviewPosts: vi.fn(),
  submitFeedback: vi.fn(),
}))
const onboardingMock = vi.hoisted(() => ({
  getOnboarding: vi.fn(),
}))
const regenerationMock = vi.hoisted(() => ({
  setRegenerationOption: vi.fn(),
}))

vi.mock("react-router-dom", () => ({
  useNavigate: () => navigateMock,
  useLocation: () => ({ state: locationState.current }),
}))

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (_key: string, fallback: string) => fallback,
  }),
}))

vi.mock("@/hooks/use-toast", () => ({
  useToast: () => ({ toast: toastMock }),
}))

vi.mock("@/services/chatService", () => chatServiceMock)
vi.mock("@/services/onboardingService", () => onboardingMock)
vi.mock("@/services/regenerationFlowService", () => regenerationMock)

const postGeneration: AIPostGeneration = {
  id: "gen-1",
  posts: ["Post 1", "Post 2", "Post 3", "Post 4", "Post 5"],
  edit_count: 0,
  has_images: false,
  posts_review_complete: false,
  images_status: "not_started",
  images_generation_started_at: null,
  images_generation_completed_at: null,
  created_at: "2026-07-17T00:00:00Z",
}

describe("useChatController", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    locationState.current = undefined
    onboardingMock.getOnboarding.mockResolvedValue({ business_name: "Vitamin" })
    chatServiceMock.getPremiumPosts.mockResolvedValue({ post_generation: null })
    chatServiceMock.shouldReviewPosts.mockReturnValue(true)
  })

  it("redirects to onboarding when no onboarding profile exists", async () => {
    onboardingMock.getOnboarding.mockResolvedValueOnce(null)
    const { useChatController } = await import("./useChatController")

    const { result } = renderHook(() => useChatController())

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(navigateMock).toHaveBeenCalledWith("/new-onboarding")
    expect(toastMock).toHaveBeenCalledWith(
      expect.objectContaining({ title: "Onboarding Required" }),
    )
  })

  it("loads existing posts and opens review when needed", async () => {
    chatServiceMock.getPremiumPosts.mockResolvedValueOnce({ post_generation: postGeneration })
    const { useChatController } = await import("./useChatController")

    const { result } = renderHook(() => useChatController())

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.postGen).toEqual(postGeneration)
    expect(result.current.showPostReview).toBe(true)
  })

  it("generates forced posts and clears stale images", async () => {
    chatServiceMock.getPremiumPosts.mockResolvedValueOnce({ post_generation: null })
    chatServiceMock.generatePremiumPosts.mockResolvedValueOnce({
      post_generation: postGeneration,
    })
    const { useChatController } = await import("./useChatController")

    const { result } = renderHook(() => useChatController())
    await waitFor(() => expect(result.current.loading).toBe(false))

    await act(async () => {
      await result.current.handleGeneratePosts(true)
    })

    expect(chatServiceMock.generatePremiumPosts).toHaveBeenCalledWith({
      force_regenerate: true,
    })
    expect(result.current.postGen).toEqual(postGeneration)
    expect(result.current.showPostReview).toBe(true)
  })

  it("sets regeneration options before navigating to the next flow", async () => {
    const { useChatController } = await import("./useChatController")
    const { result } = renderHook(() => useChatController())
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() => result.current.handleUseNewBusinessInfo())
    expect(regenerationMock.setRegenerationOption).toHaveBeenCalledWith("new_business_info")
    expect(navigateMock).toHaveBeenCalledWith("/new-onboarding")

    act(() => result.current.handleUseExistingBusinessInfo())
    expect(regenerationMock.setRegenerationOption).toHaveBeenCalledWith("existing_business_info")
    expect(navigateMock).toHaveBeenCalledWith("/pricing")
  })
})
