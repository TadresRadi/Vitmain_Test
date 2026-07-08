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
    }
  )
)
