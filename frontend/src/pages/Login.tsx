import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { useAuthStore } from '@/store/authStore'
import { useToast } from '@/hooks/use-toast'
import { Sparkles, Loader2, Mail, RotateCw } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import api from '@/lib/axios'
import type { UsageResponse } from '@/types/api'
import GoogleAuthButton from '@/components/GoogleAuthButton'
import { sanitizeInput, isValidEmail } from '@/lib/security'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [localError, setLocalError] = useState('')
  const [needsVerification, setNeedsVerification] = useState(false)
  const [resending, setResending] = useState(false)

  const { login, error } = useAuthStore()

  const navigate = useNavigate()
  const { toast } = useToast()
  const { t } = useTranslation()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    setLoading(true)
    setLocalError('')
    setNeedsVerification(false)

    const sanitizedEmail = sanitizeInput(email, 254)

    if (!isValidEmail(sanitizedEmail)) {
      setLocalError(t('login.invalidEmail') || 'Invalid email')
      setLoading(false)
      return
    }

    if (!password.trim()) {
      setLocalError(t('login.passwordRequired') || 'Password is required')
      setLoading(false)
      return
    }

    try {
      const response = await login(sanitizedEmail, password)

      toast({
        title: t('login.welcomeBack'),
        description: t('login.loginSuccess'),
      })

      const usageRes = await api.get<UsageResponse>('/users/usage')

      if (usageRes.data.plan_slug === 'pro') {
        navigate('/support', { replace: true })
      } else if (!response.user.onboarding_completed) {
        navigate('/new-onboarding')
      } else if (usageRes.data.has_access) {
        navigate('/chat', { replace: true })
      } else {
        navigate('/pricing', { replace: true })
      }
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        t('login.invalidCredentials')

      // Check if the error is about email verification
      if (errorMsg.toLowerCase().includes('not verified') || errorMsg.toLowerCase().includes('verify')) {
        setNeedsVerification(true)
        setLocalError(errorMsg)
      } else {
        setLocalError(errorMsg)
        toast({
          title: t('login.loginFailed'),
          description: errorMsg,
          variant: 'destructive',
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleResendVerification = async () => {
    if (!email) return
    setResending(true)
    try {
      await api.post('/auth/resend-verification', { email: sanitizeInput(email, 254) })
      toast({
        title: t('common.success', 'Success'),
        description: t(
          'verifyEmail.resent',
          'If an account exists with this email, a new verification link has been sent.'
        ),
      })
      setLocalError('')
      setNeedsVerification(false)
    } catch (err: any) {
      toast({
        title: t('common.error', 'Error'),
        description: err.response?.data?.error || 'Failed to resend verification email.',
        variant: 'destructive',
      })
    } finally {
      setResending(false)
    }
  }

  const handleGoogleSuccess = async () => {
    const usageRes = await api.get<UsageResponse>('/users/usage')

    if (usageRes.data.plan_slug === 'pro') {
      navigate('/support', { replace: true })
    } else if (usageRes.data.has_access) {
      navigate('/chat', { replace: true })
    } else {
      navigate('/pricing', { replace: true })
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="flex justify-center mb-8">
          <Link to="/" className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Vitamin</span>
          </Link>
        </div>

        <Card>
          <CardHeader className="text-center">
            <CardTitle>{t('login.title')}</CardTitle>
            <CardDescription>{t('login.description')}</CardDescription>
          </CardHeader>

          <CardContent>
            <div className="space-y-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t('login.email')}</label>
                  <Input
                    type="email"
                    placeholder={t('login.emailPlaceholder')}
                    value={email}
                    disabled={loading}
                    onChange={(e) => setEmail(sanitizeInput(e.target.value, 254))}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">{t('login.password')}</label>
                  <Input
                    type="password"
                    placeholder={t('login.passwordPlaceholder')}
                    value={password}
                    disabled={loading}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>

                {(localError || error) && (
                  <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-600">
                    {localError || error}
                  </div>
                )}

                {/* Email verification required — show resend option */}
                {needsVerification && (
                  <div className="rounded-md bg-amber-50 border border-amber-200 p-4 space-y-3">
                    <div className="flex items-start gap-2">
                      <Mail className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
                      <div className="text-sm text-amber-800">
                        <p className="font-medium mb-1">
                          {t('login.verificationRequired', 'Email verification required')}
                        </p>
                        <p className="text-amber-700">
                          {t(
                            'login.verificationHelp',
                            'Check your inbox for the verification link, or resend it below.'
                          )}
                        </p>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleResendVerification}
                      disabled={resending}
                      className="w-full border-amber-300 text-amber-700 hover:bg-amber-100"
                    >
                      {resending ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <RotateCw className="h-4 w-4 mr-2" />
                      )}
                      {t('login.resendVerification', 'Resend Verification Email')}
                    </Button>
                  </div>
                )}

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {loading ? t('login.loading') || 'Signing in...' : t('login.signIn')}
                </Button>
              </form>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>

                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    {t('login.orContinueWith')}
                  </span>
                </div>
              </div>

              <GoogleAuthButton mode="login" onSuccess={handleGoogleSuccess} />
            </div>

            <p className="mt-4 text-center text-sm text-muted-foreground">
              {t('login.noAccount')}{' '}
              <Link to="/register" className="text-primary hover:underline">
                {t('login.signUp')}
              </Link>
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}