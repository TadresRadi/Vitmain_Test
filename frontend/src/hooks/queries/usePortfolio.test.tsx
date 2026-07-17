import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
}))

vi.mock('@/lib/axios', () => ({
  default: apiMock,
  api: apiMock,
}))

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

describe('portfolio query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads featured projects through React Query', async () => {
    apiMock.get.mockResolvedValueOnce({ data: [{ id: 1, title: 'Project' }] })
    const { useFeaturedProjects } = await import('./usePortfolio')

    const { result } = renderHook(() => useFeaturedProjects(), { wrapper })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual([{ id: 1, title: 'Project' }])
    expect(apiMock.get).toHaveBeenCalledWith('/portfolio/featured-projects/')
  })

  it('loads brands and Tesla client images from their public endpoints', async () => {
    const { useBrands, useTeslaClientImages } = await import('./usePortfolio')
    apiMock.get
      .mockResolvedValueOnce({ data: [{ id: 1, name: 'Brand' }] })
      .mockResolvedValueOnce({ data: [{ id: 2, title: 'Tesla' }] })

    const brands = renderHook(() => useBrands(), { wrapper })
    const tesla = renderHook(() => useTeslaClientImages(), { wrapper })

    await waitFor(() => expect(brands.result.current.isSuccess).toBe(true))
    await waitFor(() => expect(tesla.result.current.isSuccess).toBe(true))

    expect(apiMock.get).toHaveBeenNthCalledWith(1, '/portfolio/brands/')
    expect(apiMock.get).toHaveBeenNthCalledWith(2, '/portfolio/tesla-client-images/')
  })
})
