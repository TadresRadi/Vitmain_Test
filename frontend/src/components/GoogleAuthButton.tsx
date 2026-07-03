import { GoogleOAuthProvider, GoogleLogin, CredentialResponse } from '@react-oauth/google'
import { useEffect, useState } from 'react'
import { useToast } from '@/hooks/use-toast'
import { useAuthStore } from '@/store/authStore'
import { useTranslation } from 'react-i18next'
import api from '@/lib/axios'
import { Loader2 } from 'lucide-react'

interface GoogleAuthButtonProps {
  mode: 'login' | 'register'
  onSuccess?: () => void
}

export default function GoogleAuthButton({ mode, onSuccess }: GoogleAuthButtonProps) {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [googleClientId, setGoogleClientId] = useState<string>('')

  useEffect(() => {
    api.get('/auth/google/config')
      .then(res => {
        if (res.data.enabled && res.data.google_client_id) {
          setGoogleClientId(res.data.google_client_id)
        }
      })
      .catch(err => {
        console.error('Failed to fetch Google config:', err)
      })
  }, [])

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    setLoading(true)
    try {
      // Decode the JWT token to get user info
      const token = credentialResponse.credential
      if (!token) throw new Error('No credential returned')
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      const userInfo = JSON.parse(jsonPayload)

      // Send to backend
      const response = await api.post('/auth/google/callback', {
        id_token: token,
        user_info: userInfo
      })

      // Store token and update auth state
      localStorage.setItem('token', response.data.access_token)
      useAuthStore.setState({
        isAuthenticated: true,
        onboarding_completed: response.data.user.onboarding_completed
      })

      toast({
        title: mode === 'login' ? t('login.welcomeBack') : t('register.successMsg'),
        description: mode === 'login' ? t('login.loginSuccess') : t('register.googleSuccess'),
      })

      if (onSuccess) {
        onSuccess()
      }
    } catch (error: any) {
      console.error('Google auth error:', error)
      toast({
        title: t('common.error'),
        description: error.response?.data?.error || error.response?.data?.detail || t('auth.googleError'),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleError = () => {
    toast({
      title: t('common.error'),
      description: t('auth.googleError'),
      variant: 'destructive',
    })
  }

  if (!googleClientId) {
    return null // Don't render if Google OAuth is not configured
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <div className="w-full">
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          theme="outline"
          size="large"
          text={mode === 'login' ? 'signin_with' : 'signup_with'}
          shape="rectangular"
          width="100%"
          containerProps={{
            style: {
              width: '100%',
            }
          }}
        />
        {loading && (
          <div className="flex justify-center mt-2">
            <Loader2 className="h-4 w-4 animate-spin" />
          </div>
        )}
      </div>
    </GoogleOAuthProvider>
  )
}
