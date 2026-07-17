import { beforeEach, describe, expect, it, vi } from "vitest"

const chatServiceMock = vi.hoisted(() => ({
  getImagesOnlyHistory: vi.fn(),
  getPostsHistory: vi.fn(),
}))

vi.mock("@/services/chatService", () => chatServiceMock)

describe("dashboardService", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("combines posts and image history into dashboard content", async () => {
    const posts = [{ id: "post-1", post_text: "Post" }]
    const images = [{ id: "image-1", image_url: "/image.png" }]
    chatServiceMock.getPostsHistory.mockResolvedValueOnce({ posts })
    chatServiceMock.getImagesOnlyHistory.mockResolvedValueOnce({ images })

    const { getDashboardContent } = await import("./dashboardService")

    await expect(getDashboardContent()).resolves.toEqual({ posts, images })
  })

  it("falls back to empty arrays when history responses omit collections", async () => {
    chatServiceMock.getPostsHistory.mockResolvedValueOnce({})
    chatServiceMock.getImagesOnlyHistory.mockResolvedValueOnce({})

    const { getDashboardContent } = await import("./dashboardService")

    await expect(getDashboardContent()).resolves.toEqual({
      posts: [],
      images: [],
    })
  })
})
