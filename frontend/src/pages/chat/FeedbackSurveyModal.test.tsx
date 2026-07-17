import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { FeedbackPayload } from '@/types/api'
import { FeedbackSurveyModal } from './FeedbackSurveyModal'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, fallback: string) => fallback,
  }),
}))

const baseFeedback: FeedbackPayload = {
  overallSatisfaction: 0,
  postsSatisfaction: 0,
  imagesSatisfaction: 0,
  suggestions: '',
}

describe('FeedbackSurveyModal', () => {
  it('does not render when closed', () => {
    render(
      <FeedbackSurveyModal
        open={false}
        submitted={false}
        feedbackData={baseFeedback}
        setFeedbackData={vi.fn()}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />
    )

    expect(screen.queryByText('Feedback Survey')).not.toBeInTheDocument()
  })

  it('requires all ratings before submitting', () => {
    const onSubmit = vi.fn()

    render(
      <FeedbackSurveyModal
        open
        submitted={false}
        feedbackData={{ ...baseFeedback, overallSatisfaction: 7, postsSatisfaction: 8 }}
        setFeedbackData={vi.fn()}
        onClose={vi.fn()}
        onSubmit={onSubmit}
      />
    )

    const submit = screen.getByRole('button', { name: 'Submit Feedback' })
    expect(submit).toBeDisabled()
    fireEvent.click(submit)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('updates ratings and suggestions through callbacks', () => {
    const setFeedbackData = vi.fn()

    render(
      <FeedbackSurveyModal
        open
        submitted={false}
        feedbackData={baseFeedback}
        setFeedbackData={setFeedbackData}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />
    )

    fireEvent.click(screen.getAllByRole('button', { name: '5' })[0])
    fireEvent.change(screen.getByPlaceholderText('Share your thoughts...'), {
      target: { value: 'More export options' },
    })

    expect(setFeedbackData).toHaveBeenCalledTimes(2)
  })

  it('shows the submitted thank-you state', () => {
    render(
      <FeedbackSurveyModal
        open
        submitted
        feedbackData={baseFeedback}
        setFeedbackData={vi.fn()}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />
    )

    expect(screen.getByText('Thank you for your feedback!')).toBeInTheDocument()
  })
})
