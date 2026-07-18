export interface UsageResponse {
  has_access: boolean
  plan_slug: string | null
}

export interface ProfileResponse {
  id: string
  email: string
  full_name: string | null
  phone_number?: string | null
  dob?: string | null
  user_type?: string
  role: string
  is_active: boolean
  language?: string
  onboarding_completed?: boolean
  auth_provider?: string
  profile_picture?: string
}

export interface LoginUser {
  id: string
  email: string
  role: string
  full_name: string | null
  is_active?: boolean
  onboarding_completed: boolean
  is_email_verified?: boolean
  auth_provider?: string
  profile_picture?: string
}

export interface LoginResponse {
  access_token: string
  // refresh_token is no longer in the response body — it's in an httpOnly cookie
  access: string
  user: LoginUser
}

export interface ApiError {
  response?: {
    status: number
    data?: {
      detail?: string
      message?: string
      error?: string
    }
  }
  message: string
}

export type ImageGenerationStatus = 'not_started' | 'processing' | 'completed' | 'failed'

export interface AIPostGeneration {
  id: string
  posts: string[]
  edit_count: number
  has_images: boolean
  posts_review_complete: boolean
  images_status: ImageGenerationStatus
  images_generation_started_at: string | null
  images_generation_completed_at: string | null
  created_at: string
}

export interface GeneratedImage {
  id: string
  image_url: string
  image_path: string
  created_at: string
}

export interface GeneratedPost {
  id: string
  post_index: number
  post_text: string
  created_at: string
  images?: GeneratedImage[]
}

export interface GenerationSession {
  id: string
  post_generation: string | AIPostGeneration
  posts: GeneratedPost[]
  created_at: string
}

export interface PostWithImage {
  post_index: number
  text: string
  image_url: string | null
}

export interface PremiumPostsResponse {
  post_generation: AIPostGeneration | null
  posts?: string[]
  message?: string
  ai_generated?: boolean
  ai_error?: string | null
}

export interface GenerateImagesResponse {
  post_generation: AIPostGeneration
  posts_with_images: PostWithImage[]
}

export interface RegeneratePostsResponse {
  posts: string[]
  post_generation: AIPostGeneration
}

export interface CompletePostReviewResponse {
  post_generation: AIPostGeneration
}

export interface ImagesHistoryResponse {
  sessions: GenerationSession[]
}

export interface PostsHistoryResponse {
  posts: GeneratedPost[]
}

export interface ImagesOnlyHistoryResponse {
  images: GeneratedImage[]
}

export interface OnboardingResponse {
  id?: number
  business_name: string
  governorate: string | null
  business_type: string
  business_subtype: string | null
  business_type_other: string | null
  marketing_goals: string[]
  target_audience: string
  target_audience_other: string | null
  tone_of_voice: string
  tone_of_voice_other: string | null
  is_active?: boolean
  created_at?: string
}

export interface SaveOnboardingResponse {
  message?: string
  onboarding?: OnboardingResponse
}

export interface FeedbackPayload {
  overallSatisfaction: number
  postsSatisfaction: number
  imagesSatisfaction: number
  suggestions: string
}
