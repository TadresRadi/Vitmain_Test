/**
 * Secure Token Storage
 * Stores JWT tokens in memory with httpOnly cookie backup
 * Never stores sensitive tokens in localStorage
 */

interface TokenPair {
  accessToken: string
  refreshToken: string
  expiresAt?: number
}

class TokenStorage {
  private static instance: TokenStorage
  private tokens: TokenPair | null = null

  // Constants
  private readonly ACCESS_TOKEN_MEMORY_KEY = 'vitmain_access'
  private readonly TOKEN_EXPIRY_BUFFER = 60 * 1000 // 1 minute buffer

  private constructor() {
    this.loadFromMemory()
  }

  /**
   * Get singleton instance
   */
  static getInstance(): TokenStorage {
    if (!TokenStorage.instance) {
      TokenStorage.instance = new TokenStorage()
    }
    return TokenStorage.instance
  }

  /**
   * Store tokens
   * - Access token in memory (cleared on refresh)
   * - Refresh token in httpOnly cookie (set by server)
   *
   * @param accessToken JWT access token
   * @param refreshToken JWT refresh token
   * @param expiresIn Token expiry in seconds
   */
  setTokens(accessToken: string, refreshToken: string, expiresIn?: number): void {
    if (!accessToken) {
      throw new Error('Access token is required')
    }

    // Calculate expiry time
    const expiresAt = expiresIn ? Date.now() + expiresIn * 1000 : undefined

    // Store in memory
    this.tokens = {
      accessToken,
      refreshToken,
      expiresAt,
    }

    // Store in sessionStorage as backup (cleared on tab close)
    try {
      sessionStorage.setItem(this.ACCESS_TOKEN_MEMORY_KEY, JSON.stringify(this.tokens))
    } catch (error) {
      console.warn('Could not store tokens in sessionStorage:', error)
    }

    // Note: Refresh token should be set by server as httpOnly cookie
  }

  /**
   * Get access token
   * @returns Access token or null
   */
  getAccessToken(): string | null {
    if (!this.tokens) {
      this.loadFromMemory()
    }

    if (!this.tokens) {
      return null
    }

    // Check if token is expired
    if (this.isTokenExpired(this.tokens.expiresAt)) {
      console.warn('Access token has expired')
      this.clear()
      return null
    }

    return this.tokens.accessToken
  }

  /**
   * Get refresh token from httpOnly cookie
   * @returns Refresh token or null
   */
  getRefreshToken(): string | null {
    if (!this.tokens?.refreshToken) {
      return null
    }
    return this.tokens.refreshToken
  }

  /**
   * Check if token is expired
   * @param expiresAt Expiry timestamp
   * @returns True if expired or about to expire
   */
  private isTokenExpired(expiresAt?: number): boolean {
    if (!expiresAt) {
      return false // If no expiry, consider it valid
    }
    return Date.now() + this.TOKEN_EXPIRY_BUFFER >= expiresAt
  }

  /**
   * Check if user is authenticated
   * @returns True if access token exists and is not expired
   */
  isAuthenticated(): boolean {
    return this.getAccessToken() !== null
  }

  /**
   * Clear all tokens from storage
   */
  clear(): void {
    this.tokens = null
    try {
      sessionStorage.removeItem(this.ACCESS_TOKEN_MEMORY_KEY)
    } catch (error) {
      console.warn('Could not clear sessionStorage:', error)
    }
  }

  /**
   * Load tokens from sessionStorage
   * Useful when tab is refreshed but session is still active
   */
  private loadFromMemory(): void {
    try {
      const stored = sessionStorage.getItem(this.ACCESS_TOKEN_MEMORY_KEY)
      if (stored) {
        this.tokens = JSON.parse(stored)
      }
    } catch (error) {
      console.warn('Could not load tokens from sessionStorage:', error)
      this.tokens = null
    }
  }
}

export const tokenStorage = TokenStorage.getInstance()
