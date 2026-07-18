/**
 * Tests for TokenStorage singleton (httpOnly cookie variant).
 *
 * Verifies that:
 * - Access token is stored in memory + sessionStorage (NOT localStorage)
 * - Refresh token is NEVER stored in JavaScript (it's in httpOnly cookie)
 * - Tokens are cleared properly
 * - No getRefreshToken method exists (security: JS cannot read refresh token)
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { tokenStorage } from './token-storage'

describe('TokenStorage', () => {
  beforeEach(() => {
    sessionStorage.clear()
    localStorage.clear()
    tokenStorage.clear()
  })

  it('stores and retrieves access token', () => {
    tokenStorage.setAccessToken('access123')
    expect(tokenStorage.getAccessToken()).toBe('access123')
  })

  it('throws if access token is empty', () => {
    expect(() => tokenStorage.setAccessToken('')).toThrow('Access token is required')
  })

  it('clears the access token', () => {
    tokenStorage.setAccessToken('access123')
    expect(tokenStorage.getAccessToken()).toBe('access123')

    tokenStorage.clear()
    expect(tokenStorage.getAccessToken()).toBeNull()
  })

  it('isAuthenticated returns true when access token exists', () => {
    tokenStorage.setAccessToken('access123')
    expect(tokenStorage.isAuthenticated()).toBe(true)
  })

  it('isAuthenticated returns false when cleared', () => {
    tokenStorage.clear()
    expect(tokenStorage.isAuthenticated()).toBe(false)
  })

  it('does NOT store tokens in localStorage', () => {
    tokenStorage.setAccessToken('access123')

    const keys = Object.keys(localStorage)
    const tokenKeys = keys.filter(
      (k) => k.includes('token') || k.includes('vitmain') || k.includes('access')
    )
    expect(tokenKeys).toHaveLength(0)
  })

  it('persists access token to sessionStorage for tab refresh', () => {
    tokenStorage.setAccessToken('access123')

    const sessionKeys = Object.keys(sessionStorage)
    expect(sessionKeys.length).toBeGreaterThan(0)
  })

  it('returns null when no token set', () => {
    expect(tokenStorage.getAccessToken()).toBeNull()
  })

  it('does NOT expose a getRefreshToken method (security)', () => {
    // The refresh token lives in an httpOnly cookie and must NEVER be
    // accessible to JavaScript. Verify the method does not exist.
    expect((tokenStorage as any).getRefreshToken).toBeUndefined()
  })

  it('does NOT expose a setTokens method (security)', () => {
    // The old setTokens method accepted a refresh token argument — it
    // must not exist anymore.
    expect((tokenStorage as any).setTokens).toBeUndefined()
  })
})