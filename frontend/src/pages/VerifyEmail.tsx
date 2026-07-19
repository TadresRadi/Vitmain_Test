import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { CheckCircle, XCircle, Loader2, Mail, RotateCw } from 'lucide-react'
import api from '@/lib/axios'
import { useToast } from '@/hooks/use-toast'
import { useTranslation } from 'react-i18next'

type VerifyStatus = 'loading' | 'success' | 'error'

export default function VerifyEmail() {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { toast } = useToast()

  const [status, setStatus] = useState<VerifyStatus>('loading')
  const [errorMessage, setErrorMessage] = useState('')
  const [resending, setResending] = useState(false)

  const token = searchParams.get('token')
  const email = searchParams.get('email')

  useEffect(() => {
    if (!token || !email) {
      setStatus('error')
      setErrorMessage('Invalid verification link. Missing token or email.')
      return
    }

    async function doVerification() {
      try {
        const response = await api.post('/auth/verify-email', { email, token })
        if (response.data.message) {
          setStatus('success')
        } else {
          setStatus('error')
          setErrorMessage('Verification failed. Please try again.')
        }
      } catch (err: any) {
        setStatus('error')
        setErrorMessage(
          err.response?.data?.error ||
          err.response?.data?.detail ||
          'Verification failed. The link may have expired.'
        )
      }
    }

    doVerification()
  }, [token, email])

  const handleResend = async () => {
    if (!email) return
    setResending(true)
    try {
      await api.post('/auth/resend-verification', { email })
      toast({
        title: t('common.success', 'Success'),
        description: t(
          'verifyEmail.resent',
          'If an account exists with this email, a new verification link has been sent.'
        ),
      })
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

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card>
          <CardContent className="pt-6 text-center">
            {status === 'loading' && (
              <>
                <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
                <h2 className="text-xl font-bold mb-2">
                  {t('verifyEmail.verifying', 'Verifying your email...')}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {t('verifyEmail.pleaseWait', 'Please wait a moment.')}
                </p>
              </>
            )}

            {status === 'success' && (
              <>
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                <h2 className="text-xl font-bold mb-2">
                  {t('verifyEmail.success', 'Email Verified!')}
                </h2>
                <p className="text-sm text-muted-foreground mb-6">
                  {t(
                    'verifyEmail.successDesc',
                    'Your email has been verified successfully. You can now log in to your account.'
                  )}
                </p>
                <Button onClick={() => navigate('/login')} className="w-full">
                  {t('verifyEmail.goToLogin', 'Go to Login')}
                </Button>
              </>
            )}

            {status === 'error' && (
              <>
                <XCircle className="h-12 w-12 mx-auto mb-4 text-red-500" />
                <h2 className="text-xl font-bold mb-2">
                  {t('verifyEmail.failed', 'Verification Failed')}
                </h2>
                <p className="text-sm text-muted-foreground mb-6">{errorMessage}</p>

                {email && (
                  <div className="space-y-3">
                    <Button
                      onClick={handleResend}
                      disabled={resending}
                      variant="outline"
                      className="w-full"
                    >
                      {resending ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <RotateCw className="h-4 w-4 mr-2" />
                      )}
                      {t('verifyEmail.resend', 'Resend Verification Email')}
                    </Button>

                    <div className="text-sm text-muted-foreground">
                      <Mail className="h-4 w-4 inline mr-1" />
                      {email}
                    </div>
                  </div>
                )}

                <div className="mt-6 pt-6 border-t">
                  <Link to="/login" className="text-sm text-primary hover:underline">
                    {t('verifyEmail.backToLogin', 'Back to Login')}
                  </Link>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}