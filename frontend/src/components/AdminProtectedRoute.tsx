import { Navigate } from 'react-router-dom'
import { useAdminAuthStore } from '@/store/adminAuthStore'

interface AdminProtectedRouteProps {
  children: React.ReactNode
}

export default function AdminProtectedRoute({ children }: AdminProtectedRouteProps) {
  const { isAdminAuthenticated } = useAdminAuthStore()

  if (!isAdminAuthenticated) {
    return <Navigate to="/admin-login" replace />
  }

  return <>{children}</>
}
