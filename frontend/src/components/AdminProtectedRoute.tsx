import { Navigate } from 'react-router-dom'
import { useAdminAuthStore } from '@/store/adminAuthStore'

interface AdminProtectedRouteProps {
  children: React.ReactNode
}

export default function AdminProtectedRoute({ children }: AdminProtectedRouteProps) {
  const { isAdminAuthenticated, adminToken } = useAdminAuthStore()

  console.log('AdminProtectedRoute - Auth state:', { isAdminAuthenticated, adminToken })

  if (!isAdminAuthenticated) {
    console.log('AdminProtectedRoute - Redirecting to /admin-login')
    return <Navigate to="/admin-login" replace />
  }

  console.log('AdminProtectedRoute - Rendering children')
  return <>{children}</>
}
