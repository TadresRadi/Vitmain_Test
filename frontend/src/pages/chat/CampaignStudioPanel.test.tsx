import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { AIPostGeneration } from '@/types/api'
import { CampaignStudioPanel } from './CampaignStudioPanel'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, fallback: string) => fallback,
  }),
}))

const basePostGen: AIPostGeneration = {
  id: 'gen-1',
  posts: ['Post one', 'Post two', 'Post three', 'Post four', 'Post five'],
  edit_count: 0,
  has_images: false,
  posts_review_complete: false,
  images_status: 'not_started',
  images_generation_started_at: null,
  images_generation_completed_at: null,
  created_at: '2026-07-17T00:00:00Z',
}

function renderPanel(overrides: Partial<React.ComponentProps<typeof CampaignStudioPanel>> = {}) {
  const props: React.ComponentProps<typeof CampaignStudioPanel> = {
    loading: false,
    postGen: null,
    postsWithImages: null,
    generatingPosts: false,
    generatingImages: false,
    showPostReview: false,
    showPostSelection: false,
    selectedPosts: [],
    regeneratingPosts: false,
    onGeneratePosts: vi.fn(),
    onGenerateImages: vi.fn(),
    onPostReviewYes: vi.fn(),
    onPostReviewNo: vi.fn(),
    onRegenerateSelectedPosts: vi.fn(),
    onTogglePostSelection: vi.fn(),
    onCancelPostSelection: vi.fn(),
    onOpenFeedbackSurvey: vi.fn(),
    onOpenNewPostsOptions: vi.fn(),
    ...overrides,
  }

  render(<CampaignStudioPanel {...props} />)
  return props
}

describe('CampaignStudioPanel', () => {
  it('shows the loading state', () => {
    renderPanel({ loading: true })

    expect(screen.getByText('Syncing Campaign Studio...')).toBeInTheDocument()
  })

  it('calls generate posts from the empty campaign state', () => {
    const props = renderPanel()

    fireEvent.click(screen.getByRole('button', { name: /Formulate 5 Campaign Posts/i }))

    expect(props.onGeneratePosts).toHaveBeenCalledTimes(1)
  })

  it('renders posts and post review actions', () => {
    const props = renderPanel({
      postGen: basePostGen,
      showPostReview: true,
    })

    expect(screen.getByText('Post one')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Yes' }))
    fireEvent.click(screen.getByRole('button', { name: 'No' }))

    expect(props.onPostReviewYes).toHaveBeenCalledTimes(1)
    expect(props.onPostReviewNo).toHaveBeenCalledTimes(1)
  })

  it('shows image generation after review completion', () => {
    const props = renderPanel({
      postGen: { ...basePostGen, posts_review_complete: true },
    })

    fireEvent.click(screen.getByRole('button', { name: 'Generate Images' }))

    expect(props.onGenerateImages).toHaveBeenCalledTimes(1)
  })

  it('shows bottom actions when images exist', () => {
    const props = renderPanel({
      postGen: { ...basePostGen, has_images: true, posts_review_complete: true },
    })

    fireEvent.click(screen.getByRole('button', { name: 'Feedback Survey' }))
    fireEvent.click(screen.getByRole('button', { name: 'Generate New Posts and Images' }))

    expect(props.onOpenFeedbackSurvey).toHaveBeenCalledTimes(1)
    expect(props.onOpenNewPostsOptions).toHaveBeenCalledTimes(1)
  })
})
