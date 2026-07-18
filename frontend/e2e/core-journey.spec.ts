import { test, expect, type Page } from '@playwright/test'

/**
 * Core user journey E2E test.
 *
 * Smoke tests for page loads, protected route redirects, and backend health.
 * The full registration + email verification + onboarding flow is deferred
 * to Phase 3 (requires admin user-creation endpoint or email interception).
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend running on http://localhost
 */

const API_URL = 'http://localhost:8000/api'

async function registerUser(page: Page, email: string, password: string) {
  await page.goto('/register')

  // Full Name (first text input — no type attribute defaults to text)
  await page.locator('input:not([type])').first().fill('E2E Test User')

  // Email
  await page.fill('input[type="email"]', email)

  // Phone
  await page.fill('input[type="tel"]', '01012345678')

  // Date of birth
  await page.fill('input[type="date"]', '1990-01-01')

  // User type select — default "explorer" is fine, no action needed

  // Password (first) + Confirm password (second)
  const passwordInputs = page.locator('input[type="password"]')
  await passwordInputs.nth(0).fill(password)
  await passwordInputs.nth(1).fill(password)

  await page.click('button[type="submit"]')

  // After registration, user is redirected to /login (email verification required)
  await page.waitForURL(/\/login/, { timeout: 15_000 })
}
test.describe('Core user journey', () => {
    test('unverified user cannot log in', async ({ page }) => {
    const email = `e2e-unverified-${Date.now()}@example.com`
    const password = 'TestPass123!'

    // Register — redirects to /login after success
    await registerUser(page, email, password)

    // Now on /login page — try to log in with the unverified credentials
    await page.waitForSelector('input[type="email"]', { timeout: 10_000 })
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button[type="submit"]')

    // Should show error about email not being verified.
    // The error appears in a toast notification (red bg) or inline error div.
    // Wait for either the toast text or the inline error.
    const errorLocator = page.locator('text=/not verified/i').first()
    await expect(errorLocator).toBeVisible({ timeout: 15_000 })
  })

  test('verified user can log in and complete onboarding', async ({ request }) => {
    // Placeholder — full implementation deferred to Phase 3.
    // Requires admin user-creation endpoint or email interception (MailHog).
    const adminLoginResp = await request.post(`${API_URL}/admin/auth/login`, {
      data: {
        email: process.env.ADMIN_EMAIL || 'admin@vitmain.com',
        password: process.env.ADMIN_PASSWORD || 'admin',
      },
    })

    if (!adminLoginResp.ok()) {
      test.skip(true, 'No admin credentials available — skipping verified-user test')
      return
    }

    test.skip(true, 'Requires admin user-creation endpoint or email interception — deferred to Phase 3')
  })

  test('pricing page is accessible without login', async ({ page }) => {
    await page.goto('/pricing')
    await expect(page).toHaveURL(/\/pricing/)
    await expect(page.locator('text=/basic|pro|premium/i').first()).toBeVisible()
  })

  test('landing page loads', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/\/$/)
  })

  test('about page loads', async ({ page }) => {
    await page.goto('/about')
    await expect(page).toHaveURL(/\/about/)
  })

  test('contact page loads', async ({ page }) => {
    await page.goto('/contact')
    await expect(page).toHaveURL(/\/contact/)
  })

  test('login page loads', async ({ page }) => {
    await page.goto('/login')
    await expect(page).toHaveURL(/\/login/)
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
  })

  test('register page loads', async ({ page }) => {
    await page.goto('/register')
    await expect(page).toHaveURL(/\/register/)
    await expect(page.locator('input[type="email"]')).toBeVisible()
  })

  test('admin login page loads', async ({ page }) => {
    await page.goto('/admin-login')
    await expect(page).toHaveURL(/\/admin-login/)
  })

  test('protected routes redirect to login when unauthenticated', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/login/)

    await page.goto('/chat')
    await expect(page).toHaveURL(/\/login/)

    await page.goto('/subscription')
    await expect(page).toHaveURL(/\/login/)
  })

  test('admin route redirects to Django admin login when not authenticated', async ({ page }) => {
    // /admin is proxied to Django's admin (via nginx), which requires
    // staff login. Unauthenticated users get redirected to /admin/login/.
    await page.goto('/admin')
    await expect(page).toHaveURL(/\/admin\/login/)
  })
})

test.describe('Smoke tests (require running stack)', () => {
  test('backend health endpoint returns 200', async ({ request }) => {
    const resp = await request.get('http://localhost:8000/health/')
    expect(resp.status()).toBe(200)
    const data = await resp.json()
    expect(data.status).toBe('healthy')
  })


})