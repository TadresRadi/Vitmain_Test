import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { adminLogin as adminLoginRequest, getAdminProfile } from '@/services/authService'
import { tokenStorage } from '@/lib/token-storage'

interface AdminAuthState {
  isAdminAuthenticated: boolean
  adminToken: string | null
  adminUser: {
    id: string
    email: string
    role: string
  } | null
  adminLogin: (email: string, password: string) => Promise<void>
  adminLogout: () => void
  fetchAdminProfile: () => Promise<void>
}

export const useAdminAuthStore = create<AdminAuthState>()(
  persist(
    (set) => ({
      isAdminAuthenticated: false,
      adminToken: null,
      adminUser: null,

      adminLogin: async (email: string, password: string) => {
        try {
          const data = await adminLoginRequest(email, password)
          
          // Store token in both admin store and regular token storage for axios interceptor
          tokenStorage.setTokens(data.access_token, data.refresh_token)
          
          set({
            isAdminAuthenticated: true,
            adminToken: data.access_token,
            adminUser: {
              id: data.user.id,
              email: data.user.email,
              role: data.user.role,
            },
          })
        } catch (error) {
          throw error
        }
      },

      adminLogout: () => {
        // Clear token from regular token storage as well
        tokenStorage.clear()
        set({
          isAdminAuthenticated: false,
          adminToken: null,
          adminUser: null,
        })
      },

      fetchAdminProfile: async () => {
        try {
          const data = await getAdminProfile()
          
          set({
            adminUser: {
              id: data.id,
              email: data.email,
              role: data.role,
            },
          })
        } catch (error) {
          console.error('Failed to fetch admin profile:', error)
        }
      },
    }),
    {
      name: 'admin-auth-storage',
      // Hydrate tokenStorage from persisted admin state after rehydration.
      // This ensures the axios interceptors will attach Authorization headers
      // on page load without requiring a manual console injection.
      onRehydrateStorage: () => (persistedState) => {
        try {
          if (!persistedState) return
          // persistedState shape may vary depending on persist implementation/version.
          // Try a few potential locations for the adminToken.
          const maybeToken =
            (persistedState as any).adminToken ??
            (persistedState as any).state?.adminToken ??
            (persistedState as any).state?.state?.adminToken

          if (maybeToken) {
            // Refresh token is usually handled via httpOnly cookie by the server.
            // Passing empty string for refreshToken here is acceptable for header hydration.
            tokenStorage.setTokens(maybeToken, '')
            // (Optional) mark admin as authenticated in store if not already set
            // but persist will rehydrate the state itself; tokenStorage hydration is the main goal.
          }
        } catch (e) {
          // Fail silently; don't block app boot on hydration errors.
          // eslint-disable-next-line no-console
          console.warn('Admin token hydration skipped:', e)
        }
      },
    }
  )
)