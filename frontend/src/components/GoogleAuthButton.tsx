// frontend/src/components/GoogleAuthButton.tsx
import { GoogleLogin, CredentialResponse } from '@react-oauth/google'
import { useState } from 'react'
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

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    setLoading(true)
    try {
      const token = credentialResponse.credential
      if (!token) throw new Error('No credential returned')

      const payload: Record<string, string> = {}
      payload['id_token'] = token

      // Send payload to backend for verification
      const response = await api.post('/auth/google/callback', payload)

      const { setTokens, setUser } = useAuthStore.getState()
      setTokens(
        response.data.access_token,
        response.data.refresh_token
      )
      setUser(response.data.user)

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

  // Render only if root provider initialized (main.tsx sets this flag)
  const providerAvailable = typeof window !== 'undefined' && (window as any).__VITMAIN_GOOGLE_OAUTH__

  if (!providerAvailable) {
    return null
  }

  return (
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
  )
}