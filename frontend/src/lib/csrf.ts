/**
 * CSRF Token Management
 * Handles generation and storage of CSRF tokens for API requests
 */

import axios, { AxiosInstance } from 'axios'

const CSRF_TOKEN_HEADER = 'X-CSRF-Token'
const CSRF_COOKIE_NAME = 'csrftoken'

export class CSRFTokenService {
  private static instance: CSRFTokenService
  private axiosInstance: AxiosInstance

  private constructor() {
    this.axiosInstance = axios.create()
  }

  /**
   * Get singleton instance
   */
  static getInstance(): CSRFTokenService {
    if (!CSRFTokenService.instance) {
      CSRFTokenService.instance = new CSRFTokenService()
    }
    return CSRFTokenService.instance
  }

  /**
   * Get CSRF token from cookie
   * @returns CSRF token or null if not found
   */
  getTokenFromCookie(): string | null {
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === CSRF_COOKIE_NAME) {
        return decodeURIComponent(value)
      }
    }
    return null
  }

  /**
   * Get or fetch CSRF token from server
   * @returns CSRF token
   */
  async getToken(): Promise<string> {
    // First try to get from cookie
    let token = this.getTokenFromCookie()
    if (token) {
      return token
    }

    // If not in cookie, fetch from server
    try {
      const response = await this.axiosInstance.get('/api/auth/csrf-token/')
      token = response.data.csrfToken
      if (token) {
        return token
      }
    } catch (error) {
      console.warn('Failed to fetch CSRF token:', error)
    }

    throw new Error('CSRF token not available')
  }

  /**
   * Add CSRF token to request headers
   * @param headers Request headers object
   */
  async addTokenToHeaders(
    headers: Record<string, string>
  ): Promise<Record<string, string>> {
    try {
      const token = await this.getToken()
      headers[CSRF_TOKEN_HEADER] = token
      return headers
    } catch (error) {
      console.warn('Could not add CSRF token:', error)
      return headers
    }
  }

  /**
   * Clear CSRF token
   */
  clearToken(): void {
    // Set cookie to expire
    document.cookie = `${CSRF_COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
  }
}

export const csrfTokenService = CSRFTokenService.getInstance()