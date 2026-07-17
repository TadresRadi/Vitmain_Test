import api from '@/lib/axios'
import type { OnboardingResponse, SaveOnboardingResponse } from '@/types/api'

export interface OnboardingFormData {
  businessName: string
  governorate: string
  businessType: string
  businessSubtype: string
  businessTypeOther: string
  marketingGoals: string[]
  targetAudience: string
  targetAudienceOther: string
  toneOfVoice: string
  toneOfVoiceOther: string
}

export interface SaveOnboardingPayload {
  data: OnboardingFormData
  createNew: boolean
}

export async function getOnboarding(): Promise<OnboardingResponse> {
  const response = await api.get<OnboardingResponse>('/onboarding/')
  return response.data
}

export async function saveOnboarding({
  data,
  createNew,
}: SaveOnboardingPayload): Promise<SaveOnboardingResponse> {
  const payload = {
    business_name: data.businessName,
    governorate: data.governorate,
    business_type: data.businessType,
    business_subtype: data.businessSubtype || null,
    business_type_other: data.businessTypeOther || null,
    marketing_goals: data.marketingGoals,
    target_audience: data.targetAudience,
    target_audience_other: data.targetAudienceOther || null,
    tone_of_voice: data.toneOfVoice,
    tone_of_voice_other: data.toneOfVoiceOther || null,
    create_new: createNew,
  }

  const response = await api.post<SaveOnboardingResponse>('/onboarding/', payload)
  return response.data
}
