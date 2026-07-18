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
    console.log('Fetching Google config from:', '/auth/google/config')
    api
      .get('/auth/google/config')
      .then((res) => {
        console.log('Google config response:', res.data)
        if (res.data.enabled && res.data.google_client_id) {
          console.log('Setting Google Client ID:', res.data.google_client_id)
          setGoogleClientId(res.data.google_client_id)
        } else {
          console.warn('Google config disabled or missing client ID')
        }
      })
      .catch((err) => {
        console.error('Failed to fetch Google config:', err)
      })
  }, [])

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    setLoading(true)
    try {
      const token = credentialResponse.credential
      if (!token) throw new Error('No credential returned')

      // Use the store action which handles token storage correctly
      // (access token in memory + sessionStorage, refresh token in httpOnly cookie)
      const success = await useAuthStore.getState().loginWithGoogle(token)
      if (!success) {
        throw new Error('Google authentication failed')
      }

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
        description:
          error.response?.data?.error || error.response?.data?.detail || t('auth.googleError'),
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
      <div className="flex justify-center w-full">
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          theme="outline"
          size="large"
          text={mode === 'login' ? 'signin_with' : 'signup_with'}
          shape="rectangular"
          width={400}
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
