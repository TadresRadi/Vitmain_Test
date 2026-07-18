/**
 * Secure Axios Instance
 * Configured with security headers and token management
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
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
        // Don't hardcode Content-Type here — axios sets it automatically:
        //   - "application/json" for plain objects
        //   - "multipart/form-data; boundary=..." for FormData
        // Hardcoding "application/json" here breaks FormData uploads because
        // it overrides the multipart Content-Type.
        'X-Requested-With': 'XMLHttpRequest',
      },
    })

    // Request interceptor - add auth token
    instance.interceptors.request.use(
      async (config) => {
        // If the body is FormData, DELETE the hardcoded Content-Type header
        // so axios can set "multipart/form-data; boundary=..." automatically.
        // The instance default is "application/json" (set above), which would
        // otherwise override the multipart Content-Type and break file uploads.
        const isFormData = typeof FormData !== 'undefined' && config.data instanceof FormData

        if (isFormData) {
          delete config.headers['Content-Type']
          delete config.headers?.['content-type']
        }

        // Add CSRF token (without clobbering existing headers)
        try {
          const token = await csrfTokenService.getToken()
          if (token) {
            config.headers['X-CSRFToken'] = token
          }
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
    // The refresh token is in an httpOnly cookie, automatically sent via
    // withCredentials: true. No need to read it from storage or send it
    // in the request body.
    instance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          // If the refresh endpoint itself returned 401, the cookie is
          // invalid/expired — redirect to login.
          if (originalRequest.url?.includes('/auth/refresh')) {
            tokenStorage.clear()
            window.location.href = '/login'
            return Promise.reject(error)
          }

          originalRequest._retry = true

          try {
            // Call refresh — refresh token is sent automatically via cookie
            const response = await instance.post('auth/refresh', {})

            if (response.data.access) {
              // Store the new access token
              tokenStorage.setAccessToken(response.data.access)

              // Retry original request with new access token
              originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`
              return instance(originalRequest)
            }
          } catch (refreshError) {
            // Refresh failed — clear token and redirect to login
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
  async post<T>(url: string, data?: Record<string, any>, config?: AxiosRequestConfig) {
    return this.axiosInstance.post<T>(url, data, config)
  }

  /**
   * Make PUT request
   */
  async put<T>(url: string, data?: Record<string, any>, config?: AxiosRequestConfig) {
    return this.axiosInstance.put<T>(url, data, config)
  }

  /**
   * Make PATCH request
   */
  async patch<T>(url: string, data?: Record<string, any>, config?: AxiosRequestConfig) {
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
