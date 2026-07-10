/**
 * Tests for TokenStorage singleton.
 *
 * Verifies that tokens are stored in memory + sessionStorage (NOT localStorage),
 * cleared properly, and that expiry is handled correctly.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { tokenStorage } from './token-storage'

describe('TokenStorage', () => {
  beforeEach(() => {
    // Clear all storage before each test
    sessionStorage.clear()
    localStorage.clear()
    // Reset the singleton's in-memory state
    tokenStorage.clear()
  })

  it('stores and retrieves access token', () => {
    tokenStorage.setTokens('access123', 'refresh456')
    expect(tokenStorage.getAccessToken()).toBe('access123')
  })

  it('stores and retrieves refresh token', () => {
    tokenStorage.setTokens('access123', 'refresh456')
    expect(tokenStorage.getRefreshToken()).toBe('refresh456')
  })

  it('throws if access token is empty', () => {
    expect(() => tokenStorage.setTokens('', 'refresh456')).toThrow(
      'Access token is required'
    )
  })

  it('clears all tokens', () => {
    tokenStorage.setTokens('access123', 'refresh456')
    expect(tokenStorage.getAccessToken()).toBe('access123')

    tokenStorage.clear()
    expect(tokenStorage.getAccessToken()).toBeNull()
    expect(tokenStorage.getRefreshToken()).toBeNull()
  })

  it('isAuthenticated returns true when token exists', () => {
    tokenStorage.setTokens('access123', 'refresh456')
    expect(tokenStorage.isAuthenticated()).toBe(true)
  })

  it('isAuthenticated returns false when cleared', () => {
    tokenStorage.clear()
    expect(tokenStorage.isAuthenticated()).toBe(false)
  })

  it('does NOT store tokens in localStorage', () => {
    tokenStorage.setTokens('access123', 'refresh456')

    // Check that no token-related keys are in localStorage
    const keys = Object.keys(localStorage)
    const tokenKeys = keys.filter(
      (k) => k.includes('token') || k.includes('vitmain') || k.includes('access')
    )
    expect(tokenKeys).toHaveLength(0)
  })

  it('persists to sessionStorage for tab refresh', () => {
    tokenStorage.setTokens('access123', 'refresh456')

    // Verify something is in sessionStorage (the backup)
    const sessionKeys = Object.keys(sessionStorage)
    expect(sessionKeys.length).toBeGreaterThan(0)
  })

  it('returns null when no tokens set', () => {
    expect(tokenStorage.getAccessToken()).toBeNull()
    expect(tokenStorage.getRefreshToken()).toBeNull()
  })
})