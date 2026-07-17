import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ChatPageHeader } from './ChatPageHeader'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, fallback: string) => fallback,
  }),
}))

describe('ChatPageHeader', () => {
  it('renders the chat title and assistance copy', () => {
    render(<ChatPageHeader />)

    expect(screen.getByText('Vitamin AI Premium Marketing Strategist')).toBeInTheDocument()
    expect(screen.getByText('Formulate high-conversion copy campaigns')).toBeInTheDocument()
  })
})
