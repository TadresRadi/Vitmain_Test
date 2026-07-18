/**
 * Secure Token Storage
 *
 * - Access token: in memory + sessionStorage backup (short-lived, 15 min)
 * - Refresh token: NEVER stored in JavaScript. Stored in an httpOnly
 *   cookie set by the backend, automatically sent with requests via
 *   withCredentials: true.
 *
 * This means:
 * - XSS attacks can read the access token (15 min lifetime, limited damage)
 * - XSS attacks CANNOT read or steal the refresh token (httpOnly cookie)
 * - Page refresh survives (access token in sessionStorage for up to 15 min)
 * - After 15 min, the axios interceptor calls /auth/refresh, which uses
 *   the httpOnly cookie to get a new access token
 */

interface TokenStorage {
  getAccessToken(): string | null
  setAccessToken(token: string): void
  clear(): void
  isAuthenticated(): boolean
}

class SecureTokenStorage implements TokenStorage {
  private static instance: SecureTokenStorage
  private accessToken: string | null = null
  private readonly STORAGE_KEY = 'vitmain_access_token'
  private constructor() {
    this.loadFromSession()
  }

  static getInstance(): TokenStorage {
    if (!SecureTokenStorage.instance) {
      SecureTokenStorage.instance = new SecureTokenStorage()
    }
    return SecureTokenStorage.instance
  }

  /**
   * Store the access token in memory + sessionStorage.
   * The refresh token is NOT stored here — it's in an httpOnly cookie.
   */
  setAccessToken(token: string): void {
    if (!token) {
      throw new Error('Access token is required')
    }
    this.accessToken = token
    try {
      sessionStorage.setItem(this.STORAGE_KEY, token)
    } catch (error) {
      console.warn('Could not store access token in sessionStorage:', error)
    }
  }

  getAccessToken(): string | null {
    if (!this.accessToken) {
      this.loadFromSession()
    }
    return this.accessToken
  }

  clear(): void {
    this.accessToken = null
    try {
      sessionStorage.removeItem(this.STORAGE_KEY)
    } catch (error) {
      console.warn('Could not clear sessionStorage:', error)
    }
  }

  isAuthenticated(): boolean {
    return this.getAccessToken() !== null
  }

  private loadFromSession(): void {
    try {
      const token = sessionStorage.getItem(this.STORAGE_KEY)
      if (token) {
        this.accessToken = token
      }
    } catch (error) {
      console.warn('Could not load access token from sessionStorage:', error)
      this.accessToken = null
    }
  }
}

export const tokenStorage = SecureTokenStorage.getInstance()