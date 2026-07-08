/**
 * Secure Axios Instance
 * Configured with security headers and token management
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosRequestHeaders } from 'axios'
import { tokenStorage } from './token-storage'
import { csrfTokenService } from './csrf'

function getApiBaseURL(): string {
  const configuredUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
  return configuredUrl.replace(/\/+$/, '') // Remove trailing slashes only
}

class SecureAxios {
  private static instance: SecureAxios
  private axiosInstance: AxiosInstance

  private constructor() {
    this.axiosInstance = this.createSecureInstance()
  }

  /**
   * Get singleton instance
   */
  static getInstance(): SecureAxios {
    if (!SecureAxios.instance) {
      SecureAxios.instance = new SecureAxios()
    }
    return SecureAxios.instance
  }

  /**
   * Create secure axios instance with interceptors
   */
  private createSecureInstance(): AxiosInstance {
    const instance = axios.create({
      baseURL: getApiBaseURL(),
      timeout: 30000,
      withCredentials: true, // Include cookies in requests
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
    })

    // Request interceptor - add auth token
    instance.interceptors.request.use(
      async (config) => {
        // Add CSRF token
        try {
          const headers = await csrfTokenService.addTokenToHeaders(
            config.headers as Record<string, string>
          )
          config.headers = headers as AxiosRequestHeaders
        } catch (error) {
          console.warn('Could not add CSRF token:', error)
        }

        // Add authorization header
        const token = tokenStorage.getAccessToken()
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`
        }

        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor - handle token refresh
    instance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          const refreshToken = tokenStorage.getRefreshToken()
          if (!refreshToken || originalRequest.url?.includes('/auth/refresh')) {
            return Promise.reject(error)
          }

          originalRequest._retry = true

          try {
            // Try to refresh token
            const response = await instance.post('auth/refresh', {
              refresh: refreshToken,
            })

            if (response.data.access) {
              // Update token
              tokenStorage.setTokens(
                response.data.access,
                refreshToken
              )

              // Retry original request
              originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`
              return instance(originalRequest)
            }
          } catch (refreshError) {
            // Refresh failed - logout user
            tokenStorage.clear()
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )

    return instance
  }

  /**
   * Get axios instance
   */
  getInstance(): AxiosInstance {
    return this.axiosInstance
  }

  /**
   * Make GET request
   */
  async get<T>(url: string, config?: AxiosRequestConfig) {
    return this.axiosInstance.get<T>(url, config)
  }

  /**
   * Make POST request
   */
  async post<T>(
    url: string,
    data?: Record<string, any>,
    config?: AxiosRequestConfig
  ) {
    return this.axiosInstance.post<T>(url, data, config)
  }

  /**
   * Make PUT request
   */
  async put<T>(
    url: string,
    data?: Record<string, any>,
    config?: AxiosRequestConfig
  ) {
    return this.axiosInstance.put<T>(url, data, config)
  }

  /**
   * Make PATCH request
   */
  async patch<T>(
    url: string,
    data?: Record<string, any>,
    config?: AxiosRequestConfig
  ) {
    return this.axiosInstance.patch<T>(url, data, config)
  }

  /**
   * Make DELETE request
   */
  async delete<T>(url: string, config?: AxiosRequestConfig) {
    return this.axiosInstance.delete<T>(url, config)
  }
}

export const secureAxios = SecureAxios.getInstance()
