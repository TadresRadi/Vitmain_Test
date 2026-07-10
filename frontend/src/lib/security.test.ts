/**
 * Tests for frontend security utilities.
 *
 * These functions prevent XSS, injection attacks, and other
 * frontend vulnerabilities. They must be thoroughly tested.
 */
import { describe, it, expect } from 'vitest'
import {
  escapeHtml,
  sanitizeInput,
  isValidEmail,
  validatePasswordStrength,
  isSafeURL,
  safeJsonParse,
} from './security'

// ============================================================================
// escapeHtml
// ============================================================================

describe('escapeHtml', () => {
  it('escapes < and > characters', () => {
    expect(escapeHtml('<script>')).toBe('&lt;script&gt;')
  })

  it('escapes & character', () => {
    expect(escapeHtml('a & b')).toBe('a &amp; b')
  })

  it('escapes ampersands, less-than, and greater-than', () => {
    expect(escapeHtml('a < b > c & d')).toBe('a &lt; b &gt; c &amp; d')
  })

  it('does not escape quotes (not needed for element content)', () => {
    // escapeHtml uses textContent/innerHTML which only escapes &, <, >
    // Quotes are only dangerous in attribute contexts, not element content
    expect(escapeHtml('"hello"')).toBe('"hello"')
  })

  it('returns empty string for null/undefined', () => {
    expect(escapeHtml(null as unknown as string)).toBe('')
    expect(escapeHtml(undefined as unknown as string)).toBe('')
  })

  it('returns empty string for non-string input', () => {
    expect(escapeHtml(123 as unknown as string)).toBe('')
  })

  it('passes through safe text unchanged', () => {
    expect(escapeHtml('hello world')).toBe('hello world')
  })
})

// ============================================================================
// sanitizeInput
// ============================================================================

describe('sanitizeInput', () => {
  it('removes script tags', () => {
    const result = sanitizeInput('<script>alert("xss")</script>hello')
    expect(result).not.toContain('<script>')
    expect(result).not.toContain('alert')
    expect(result).toContain('hello')
  })

  it('removes event handlers', () => {
    const result = sanitizeInput('<div onclick="alert(1)">text</div>')
    expect(result).not.toContain('onclick')
  })

  it('limits length', () => {
    const long = 'a'.repeat(200)
    const result = sanitizeInput(long, 50)
    expect(result.length).toBeLessThanOrEqual(50)
  })

  it('returns empty string for null/undefined', () => {
    expect(sanitizeInput(null as unknown as string)).toBe('')
  })

  it('escapes HTML after sanitizing', () => {
    const result = sanitizeInput('<b>bold</b>')
    // Should be escaped, not raw HTML
    expect(result).not.toContain('<b>')
  })
})

// ============================================================================
// isValidEmail
// ============================================================================

describe('isValidEmail', () => {
  it('accepts valid emails', () => {
    expect(isValidEmail('user@example.com')).toBe(true)
    expect(isValidEmail('test.user@domain.org')).toBe(true)
    expect(isValidEmail('a@b.co')).toBe(true)
  })

  it('rejects emails without @', () => {
    expect(isValidEmail('userexample.com')).toBe(false)
  })

  it('rejects emails without domain', () => {
    expect(isValidEmail('user@')).toBe(false)
  })

  it('rejects emails without TLD', () => {
    expect(isValidEmail('user@example')).toBe(false)
  })

  it('rejects emails with spaces', () => {
    expect(isValidEmail('user @example.com')).toBe(false)
  })

  it('rejects empty string', () => {
    expect(isValidEmail('')).toBe(false)
  })
})

// ============================================================================
// validatePasswordStrength
// ============================================================================

describe('validatePasswordStrength', () => {
  it('rejects empty password', () => {
    const result = validatePasswordStrength('')
    expect(result.isStrong).toBe(false)
    expect(result.score).toBe(0)
    expect(result.errors).toContain('Password is required')
  })

  it('rejects password shorter than 8 chars', () => {
    const result = validatePasswordStrength('Ab1!xyz')
    expect(result.isStrong).toBe(false)
    expect(result.errors).toContain('At least 8 characters')
  })

  it('rejects password without uppercase', () => {
    const result = validatePasswordStrength('abcdef1!')
    expect(result.errors).toContain('At least one uppercase letter')
  })

  it('rejects password without lowercase', () => {
    const result = validatePasswordStrength('ABCDEF1!')
    expect(result.errors).toContain('At least one lowercase letter')
  })

  it('rejects password without number', () => {
    const result = validatePasswordStrength('Abcdefg!')
    expect(result.errors).toContain('At least one number')
  })

  it('rejects password without special character', () => {
    const result = validatePasswordStrength('Abcdefg1')
    expect(result.errors).toContain('At least one special character (!@#$%^&*)')
  })

  it('accepts strong password', () => {
    const result = validatePasswordStrength('StrongP@ss1')
    expect(result.isStrong).toBe(true)
    expect(result.errors).toHaveLength(0)
    expect(result.score).toBe(100)
  })

  it('scores partially strong passwords', () => {
    // Has length, upper, lower, number — missing special char
    const result = validatePasswordStrength('Abcdefg1')
    expect(result.score).toBe(80)
    expect(result.isStrong).toBe(false)
  })
})

// ============================================================================
// isSafeURL
// ============================================================================

describe('isSafeURL', () => {
  it('rejects javascript: URLs', () => {
    expect(isSafeURL('javascript:alert(1)')).toBe(false)
  })

  it('rejects data: URLs', () => {
    expect(isSafeURL('data:text/html,<script>alert(1)</script>')).toBe(false)
  })

  it('rejects vbscript: URLs', () => {
    expect(isSafeURL('vbscript:msgbox(1)')).toBe(false)
  })

  it('accepts relative URLs starting with /', () => {
    expect(isSafeURL('/path/to/page')).toBe(true)
  })

  it('accepts relative URLs starting with .', () => {
    expect(isSafeURL('./page')).toBe(true)
  })

  it('rejects empty string', () => {
    expect(isSafeURL('')).toBe(false)
  })

  it('rejects null', () => {
    expect(isSafeURL(null as unknown as string)).toBe(false)
  })
})

// ============================================================================
// safeJsonParse
// ============================================================================

describe('safeJsonParse', () => {
  it('parses valid JSON', () => {
    expect(safeJsonParse('{"a":1}')).toEqual({ a: 1 })
    expect(safeJsonParse('[1,2,3]')).toEqual([1, 2, 3])
  })

  it('returns null for invalid JSON', () => {
    expect(safeJsonParse('not json')).toBeNull()
    expect(safeJsonParse('{invalid}')).toBeNull()
  })

  it('returns null for empty string', () => {
    expect(safeJsonParse('')).toBeNull()
  })
})