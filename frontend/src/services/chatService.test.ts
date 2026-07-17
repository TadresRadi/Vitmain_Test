import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { AIPostGeneration, ImagesHistoryResponse } from '@/types/api'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('@/lib/axios', () => ({
  default: apiMock,
  api: apiMock,
}))

describe('chatService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches the active premium posts', async () => {
    const data = { post_generation: null }
    apiMock.get.mockResolvedValueOnce({ data })

    const { getPremiumPosts } = await import('./chatService')

    await expect(getPremiumPosts()).resolves.toBe(data)
    expect(apiMock.get).toHaveBeenCalledWith('/chat/premium-posts')
  })

  it('sends force regeneration options when generating premium posts', async () => {
    const data = { post_generation: null }
    apiMock.post.mockResolvedValueOnce({ data })

    const { generatePremiumPosts } = await import('./chatService')

    await expect(generatePremiumPosts({ force_regenerate: true })).resolves.toBe(data)
    expect(apiMock.post).toHaveBeenCalledWith('/chat/premium-posts', {
      force_regenerate: true,
    })
  })

  it('sends the post generation id when generating images', async () => {
    const data = { post_generation: {}, posts_with_images: [] }
    apiMock.post.mockResolvedValueOnce({ data })

    const { generateImages } = await import('./chatService')

    await expect(generateImages('gen-1')).resolves.toBe(data)
    expect(apiMock.post).toHaveBeenCalledWith('/chat/generate-images', {
      post_generation_id: 'gen-1',
    })
  })

  it('maps images from the latest generation session only', async () => {
    const { mapLatestSessionImages } = await import('./chatService')
    const history: ImagesHistoryResponse = {
      sessions: [
        {
          id: 'latest',
          post_generation: 'gen-1',
          created_at: '2026-07-17T00:00:00Z',
          posts: [
            {
              id: 'post-1',
              post_index: 0,
              post_text: 'Post one',
              created_at: '2026-07-17T00:00:00Z',
              images: [
                { id: 'img-1', image_url: '/one.png', image_path: 'one.png', created_at: 'now' },
              ],
            },
            {
              id: 'post-2',
              post_index: 1,
              post_text: 'Post two',
              created_at: '2026-07-17T00:00:00Z',
              images: [],
            },
          ],
        },
        {
          id: 'older',
          post_generation: 'gen-0',
          created_at: '2026-07-16T00:00:00Z',
          posts: [],
        },
      ],
    }

    expect(mapLatestSessionImages(history)).toEqual([
      { post_index: 0, text: 'Post one', image_url: '/one.png' },
      { post_index: 1, text: 'Post two', image_url: null },
    ])
  })

  it('returns null when there is no image history session', async () => {
    const { mapLatestSessionImages } = await import('./chatService')

    expect(mapLatestSessionImages({ sessions: [] })).toBeNull()
  })

  it('requires review only before images and before review completion', async () => {
    const { shouldReviewPosts } = await import('./chatService')
    const base: AIPostGeneration = {
      id: 'gen-1',
      posts: ['1', '2', '3', '4', '5'],
      edit_count: 0,
      has_images: false,
      posts_review_complete: false,
      images_status: 'not_started',
      images_generation_started_at: null,
      images_generation_completed_at: null,
      created_at: '2026-07-17T00:00:00Z',
    }

    expect(shouldReviewPosts(base)).toBe(true)
    expect(shouldReviewPosts({ ...base, posts_review_complete: true })).toBe(false)
    expect(shouldReviewPosts({ ...base, has_images: true })).toBe(false)
  })
})
