// frontend/src/main.tsx
import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'
import './i18n'
import { GoogleOAuthProvider } from '@react-oauth/google'
import api from '@/lib/axios'

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
})

function AppWrapper() {
  const [googleClientId, setGoogleClientId] = useState<string | null>(null)
  const [loadingConfig, setLoadingConfig] = useState(true)

  useEffect(() => {
    let mounted = true
    api.get('/auth/google/config')
      .then(res => {
        if (!mounted) return
        if (res.data?.enabled && res.data?.google_client_id) {
          setGoogleClientId(res.data.google_client_id)
          // mark that provider config is available for child components
          ;(window as any).__VITMAIN_GOOGLE_OAUTH__ = true
        } else {
          setGoogleClientId(null)
          ;(window as any).__VITMAIN_GOOGLE_OAUTH__ = false
        }
      })
      .catch(err => {
        console.error('Failed to load Google OAuth config:', err)
        setGoogleClientId(null)
        ;(window as any).__VITMAIN_GOOGLE_OAUTH__ = false
      })
      .finally(() => {
        if (mounted) setLoadingConfig(false)
      })

    return () => {
      mounted = false
    }
  }, [])

  if (loadingConfig) {
    return (
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    )
  }

  if (googleClientId) {
    return (
      <GoogleOAuthProvider clientId={googleClientId}>
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </GoogleOAuthProvider>
    )
  }

  return (
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppWrapper />
  </React.StrictMode>
)