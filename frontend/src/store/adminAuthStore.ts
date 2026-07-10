import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { adminLogin as adminLoginRequest, getAdminProfile } from '@/services/authService'
import { tokenStorage } from '@/lib/token-storage'

interface AdminAuthState {
  isAdminAuthenticated: boolean
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
      adminUser: null,

      adminLogin: async (email: string, password: string) => {
        const data = await adminLoginRequest(email, password)

        // Store the actual JWT tokens via tokenStorage (in-memory +
        // sessionStorage, NOT localStorage). The axios interceptor reads
        // from tokenStorage, so this is sufficient for authenticated requests.
        tokenStorage.setTokens(data.access_token, data.refresh_token)

        set({
          isAdminAuthenticated: true,
          adminUser: {
            id: data.user.id,
            email: data.user.email,
            role: data.user.role,
          },
        })
      },

      adminLogout: () => {
        // Clear tokens from tokenStorage (memory + sessionStorage)
        tokenStorage.clear()
        set({
          isAdminAuthenticated: false,
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
      // Use sessionStorage so the persisted state (isAdminAuthenticated,
      // adminUser) is cleared when the tab closes. Critically, we use
      // `partialize` to ensure the raw JWT is NEVER persisted to storage —
      // it lives only in tokenStorage (memory + sessionStorage via
      // tokenStorage's own logic, which does NOT store in localStorage).
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        isAdminAuthenticated: state.isAdminAuthenticated,
        adminUser: state.adminUser,
      }),
    }
  )
)