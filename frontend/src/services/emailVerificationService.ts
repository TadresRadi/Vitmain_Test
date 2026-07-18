import { api } from '@/lib/axios'

export async function verifyEmail(user_id: string, token: string): Promise<void> {
  await api.post('/auth/verify-email', { user_id, token })
}

export async function resendVerification(email: string): Promise<void> {
  await api.post('/auth/resend-verification', { email })
}