# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: core-journey.spec.ts >> Core user journey >> unverified user cannot log in
- Location: e2e\core-journey.spec.ts:45:5

# Error details

```
TimeoutError: page.waitForURL: Timeout 15000ms exceeded.
=========================== logs ===========================
waiting for navigation until "load"
  navigated to "http://localhost/new-onboarding"
============================================================
```

# Page snapshot

```yaml
- generic [ref=e3]:
  - navigation [ref=e4]:
    - generic [ref=e6]:
      - link "Vitamin Vitamin" [ref=e7] [cursor=pointer]:
        - /url: /
        - img "Vitamin" [ref=e8]
        - generic [ref=e9]: Vitamin
      - generic [ref=e10]:
        - link "Home" [ref=e11] [cursor=pointer]:
          - /url: /
        - link "About Us" [ref=e12] [cursor=pointer]:
          - /url: /about
        - link "Our Work" [ref=e13] [cursor=pointer]:
          - /url: /work
        - link "Tesla Clients" [ref=e14] [cursor=pointer]:
          - /url: /tesla-clients
        - link "Pricing" [ref=e15] [cursor=pointer]:
          - /url: /pricing
        - link "Get in Touch" [ref=e16] [cursor=pointer]:
          - /url: /contact
        - link "Chat" [ref=e17] [cursor=pointer]:
          - /url: /chat
      - generic [ref=e18]:
        - button "AR" [ref=e19] [cursor=pointer]:
          - img
          - text: AR
        - button [ref=e20] [cursor=pointer]:
          - img
        - button "Dashboard" [ref=e21] [cursor=pointer]
        - button "Logout" [ref=e22] [cursor=pointer]
  - main [ref=e23]:
    - generic [ref=e26]:
      - generic [ref=e28]:
        - generic [ref=e29]: Question 1 of 6
        - generic [ref=e30]: 17%
      - generic [ref=e34]:
        - heading "What is your business name?" [level=2] [ref=e35]
        - textbox "Enter your business name" [ref=e36]
        - generic [ref=e37]:
          - button "Previous" [disabled]:
            - img
            - text: Previous
          - button "Next" [disabled]:
            - text: Next
            - img
  - contentinfo [ref=e38]:
    - generic [ref=e39]:
      - generic [ref=e40]: Vitamin
      - generic [ref=e41]:
        - link "About Us" [ref=e42] [cursor=pointer]:
          - /url: /about
        - link "Our Work" [ref=e43] [cursor=pointer]:
          - /url: /work
        - link "Pricing" [ref=e44] [cursor=pointer]:
          - /url: /pricing
        - link "Contact" [ref=e45] [cursor=pointer]:
          - /url: /contact
      - generic [ref=e46]: © 2024 Vitmain. All rights reserved.
  - region "Notifications (F8)":
    - list
```

# Test source

```ts
  1   | import { test, expect, type Page } from '@playwright/test'
  2   | 
  3   | /**
  4   |  * Core user journey E2E test.
  5   |  *
  6   |  * Smoke tests for page loads, protected route redirects, and backend health.
  7   |  * The full registration + email verification + onboarding flow is deferred
  8   |  * to Phase 3 (requires admin user-creation endpoint or email interception).
  9   |  *
  10  |  * Prerequisites:
  11  |  * - Backend running on http://localhost:8000
  12  |  * - Frontend running on http://localhost
  13  |  */
  14  | 
  15  | const API_URL = 'http://localhost:8000/api'
  16  | 
  17  | async function registerUser(page: Page, email: string, password: string) {
  18  |   await page.goto('/register')
  19  | 
  20  |   // Full Name (first text input — no type attribute defaults to text)
  21  |   await page.locator('input:not([type])').first().fill('E2E Test User')
  22  | 
  23  |   // Email
  24  |   await page.fill('input[type="email"]', email)
  25  | 
  26  |   // Phone
  27  |   await page.fill('input[type="tel"]', '01012345678')
  28  | 
  29  |   // Date of birth
  30  |   await page.fill('input[type="date"]', '1990-01-01')
  31  | 
  32  |   // User type select — default "explorer" is fine, no action needed
  33  | 
  34  |   // Password (first) + Confirm password (second)
  35  |   const passwordInputs = page.locator('input[type="password"]')
  36  |   await passwordInputs.nth(0).fill(password)
  37  |   await passwordInputs.nth(1).fill(password)
  38  | 
  39  |   await page.click('button[type="submit"]')
  40  | 
  41  |   // After registration, user is redirected to /login (email verification required)
> 42  |   await page.waitForURL(/\/login/, { timeout: 15_000 })
      |              ^ TimeoutError: page.waitForURL: Timeout 15000ms exceeded.
  43  | }
  44  | test.describe('Core user journey', () => {
  45  |     test('unverified user cannot log in', async ({ page }) => {
  46  |     const email = `e2e-unverified-${Date.now()}@example.com`
  47  |     const password = 'TestPass123!'
  48  | 
  49  |     // Register — redirects to /login after success
  50  |     await registerUser(page, email, password)
  51  | 
  52  |     // Now on /login page — try to log in with the unverified credentials
  53  |     await page.waitForSelector('input[type="email"]', { timeout: 10_000 })
  54  |     await page.fill('input[type="email"]', email)
  55  |     await page.fill('input[type="password"]', password)
  56  |     await page.click('button[type="submit"]')
  57  | 
  58  |     // Should show error about email not being verified.
  59  |     // The error appears in a toast notification (red bg) or inline error div.
  60  |     // Wait for either the toast text or the inline error.
  61  |     const errorLocator = page.locator('text=/not verified/i').first()
  62  |     await expect(errorLocator).toBeVisible({ timeout: 15_000 })
  63  |   })
  64  | 
  65  |   test('verified user can log in and complete onboarding', async ({ request }) => {
  66  |     // Placeholder — full implementation deferred to Phase 3.
  67  |     // Requires admin user-creation endpoint or email interception (MailHog).
  68  |     const adminLoginResp = await request.post(`${API_URL}/admin/auth/login`, {
  69  |       data: {
  70  |         email: process.env.ADMIN_EMAIL || 'admin@vitmain.com',
  71  |         password: process.env.ADMIN_PASSWORD || 'admin',
  72  |       },
  73  |     })
  74  | 
  75  |     if (!adminLoginResp.ok()) {
  76  |       test.skip(true, 'No admin credentials available — skipping verified-user test')
  77  |       return
  78  |     }
  79  | 
  80  |     test.skip(true, 'Requires admin user-creation endpoint or email interception — deferred to Phase 3')
  81  |   })
  82  | 
  83  |   test('pricing page is accessible without login', async ({ page }) => {
  84  |     await page.goto('/pricing')
  85  |     await expect(page).toHaveURL(/\/pricing/)
  86  |     await expect(page.locator('text=/basic|pro|premium/i').first()).toBeVisible()
  87  |   })
  88  | 
  89  |   test('landing page loads', async ({ page }) => {
  90  |     await page.goto('/')
  91  |     await expect(page).toHaveURL(/\/$/)
  92  |   })
  93  | 
  94  |   test('about page loads', async ({ page }) => {
  95  |     await page.goto('/about')
  96  |     await expect(page).toHaveURL(/\/about/)
  97  |   })
  98  | 
  99  |   test('contact page loads', async ({ page }) => {
  100 |     await page.goto('/contact')
  101 |     await expect(page).toHaveURL(/\/contact/)
  102 |   })
  103 | 
  104 |   test('login page loads', async ({ page }) => {
  105 |     await page.goto('/login')
  106 |     await expect(page).toHaveURL(/\/login/)
  107 |     await expect(page.locator('input[type="email"]')).toBeVisible()
  108 |     await expect(page.locator('input[type="password"]')).toBeVisible()
  109 |   })
  110 | 
  111 |   test('register page loads', async ({ page }) => {
  112 |     await page.goto('/register')
  113 |     await expect(page).toHaveURL(/\/register/)
  114 |     await expect(page.locator('input[type="email"]')).toBeVisible()
  115 |   })
  116 | 
  117 |   test('admin login page loads', async ({ page }) => {
  118 |     await page.goto('/admin-login')
  119 |     await expect(page).toHaveURL(/\/admin-login/)
  120 |   })
  121 | 
  122 |   test('protected routes redirect to login when unauthenticated', async ({ page }) => {
  123 |     await page.goto('/dashboard')
  124 |     await expect(page).toHaveURL(/\/login/)
  125 | 
  126 |     await page.goto('/chat')
  127 |     await expect(page).toHaveURL(/\/login/)
  128 | 
  129 |     await page.goto('/subscription')
  130 |     await expect(page).toHaveURL(/\/login/)
  131 |   })
  132 | 
  133 |   test('admin route redirects to Django admin login when not authenticated', async ({ page }) => {
  134 |     // /admin is proxied to Django's admin (via nginx), which requires
  135 |     // staff login. Unauthenticated users get redirected to /admin/login/.
  136 |     await page.goto('/admin')
  137 |     await expect(page).toHaveURL(/\/admin\/login/)
  138 |   })
  139 | })
  140 | 
  141 | test.describe('Smoke tests (require running stack)', () => {
  142 |   test('backend health endpoint returns 200', async ({ request }) => {
```