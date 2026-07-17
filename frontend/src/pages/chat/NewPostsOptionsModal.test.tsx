import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { NewPostsOptionsModal } from './NewPostsOptionsModal'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, fallback: string) => fallback,
  }),
}))

function renderModal(overrides: Partial<React.ComponentProps<typeof NewPostsOptionsModal>> = {}) {
  const props: React.ComponentProps<typeof NewPostsOptionsModal> = {
    open: true,
    onClose: vi.fn(),
    onUseExistingBusinessInfo: vi.fn(),
    onUseNewBusinessInfo: vi.fn(),
    ...overrides,
  }

  render(<NewPostsOptionsModal {...props} />)
  return props
}

describe('NewPostsOptionsModal', () => {
  it('does not render when closed', () => {
    renderModal({ open: false })

    expect(screen.queryByText('Generate New Posts and Images')).not.toBeInTheDocument()
  })

  it('calls each option handler', () => {
    const props = renderModal()

    fireEvent.click(screen.getByText('Use New Business Information'))
    fireEvent.click(screen.getByText('Use Existing Business Information'))

    expect(props.onUseNewBusinessInfo).toHaveBeenCalledTimes(1)
    expect(props.onUseExistingBusinessInfo).toHaveBeenCalledTimes(1)
  })

  it('calls close from the header button', () => {
    const props = renderModal()

    fireEvent.click(screen.getByRole('button'))

    expect(props.onClose).toHaveBeenCalledTimes(1)
  })
})
