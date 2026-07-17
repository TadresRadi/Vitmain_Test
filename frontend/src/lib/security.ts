/**
 * Frontend Security Utilities
 * Prevents XSS, injection attacks, and other frontend vulnerabilities
 */

/**
 * Escape HTML special characters to prevent XSS
 * @param unsafe Unsafe string
 * @returns Escaped string safe for HTML
 */
export function escapeHtml(unsafe: string): string {
  if (!unsafe || typeof unsafe !== 'string') {
    return ''
  }

  const div = document.createElement('div')
  div.textContent = unsafe
  return div.innerHTML
}

/**
 * Sanitize user input
 * Removes potentially dangerous characters and scripts
 * @param input User input
 * @param maxLength Maximum length
 * @returns Sanitized string
 */
export function sanitizeInput(input: string, maxLength: number = 1000): string {
  if (!input || typeof input !== 'string') {
    return ''
  }

  // Remove any script tags
  let sanitized = input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')

  // Remove event handlers
  sanitized = sanitized.replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')
  sanitized = sanitized.replace(/on\w+\s*=\s*[^\s>]*/gi, '')

  // Limit length
  sanitized = sanitized.substring(0, maxLength)

  return escapeHtml(sanitized)
}

/**
 * Validate email format
 * @param email Email to validate
 * @returns True if valid email
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate password strength
 * @param password Password to validate
 * @returns Object with validation details
 */
export function validatePasswordStrength(password: string): {
  isStrong: boolean
  errors: string[]
  score: number
} {
  const errors: string[] = []
  let score = 0

  if (!password) {
    return { isStrong: false, errors: ['Password is required'], score: 0 }
  }

  // Length check
  if (password.length >= 8) {
    score += 20
  } else {
    errors.push('At least 8 characters')
  }

  // Uppercase check
  if (/[A-Z]/.test(password)) {
    score += 20
  } else {
    errors.push('At least one uppercase letter')
  }

  // Lowercase check
  if (/[a-z]/.test(password)) {
    score += 20
  } else {
    errors.push('At least one lowercase letter')
  }

  // Number check
  if (/[0-9]/.test(password)) {
    score += 20
  } else {
    errors.push('At least one number')
  }

  // Special character check
  if (/[!@#$%^&*()_+\-=[\]{};:'",.<>?/]/.test(password)) {
    score += 20
  } else {
    errors.push('At least one special character (!@#$%^&*)')
  }

  return {
    isStrong: errors.length === 0,
    errors,
    score,
  }
}

/**
 * Encode URI component safely
 * @param str String to encode
 * @returns Encoded string
 */

/**
 * Check if URL is safe to navigate to
 * Prevents javascript: and data: URLs
 * @param url URL to check
 * @returns True if safe
 */
export function isSafeURL(url: string): boolean {
  if (!url || typeof url !== 'string') {
    return false
  }

  const trimmed = url.trim().toLowerCase()

  // Prevent javascript: URLs
  if (trimmed.startsWith('javascript:')) {
    return false
  }

  // Prevent data: URLs
  if (trimmed.startsWith('data:')) {
    return false
  }

  // Prevent vbscript: URLs
  if (trimmed.startsWith('vbscript:')) {
    return false
  }

  // Allow relative and same-origin URLs
  if (trimmed.startsWith('/') || trimmed.startsWith('.')) {
    return true
  }

  // Check if same origin
  try {
    const urlObj = new URL(url, window.location.href)
    return urlObj.origin === window.location.origin
  } catch {
    return false
  }
}

/**
 * Safely parse JSON
 * @param json JSON string
 * @returns Parsed object or null
 */
export function safeJsonParse<T = any>(json: string): T | null {
  try {
    return JSON.parse(json)
  } catch (error) {
    console.warn('Error parsing JSON:', error)
    return null
  }
}

/**
 * Generate a nonce for CSP
 * @returns Random nonce string
 */
/**
 * Generate a cryptographically secure nonce for CSP
 * Uses the Web Crypto API (window.crypto.getRandomValues).
 * Falls back to Math.random only if the Crypto API is unavailable
 * (extremely old browsers / non-secure contexts).
 * @returns Random nonce string (base36, ~17+ chars)
 */

/**
 * Content Security Policy helper
 */
