import { useCallback, useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useToast } from '@/hooks/use-toast'
import {
  completePostReview,
  generateImages as generateCampaignImages,
  generatePremiumPosts,
  getImagesHistory,
  getPremiumPosts,
  mapLatestSessionImages,
  regenerateSelectedPosts,
  shouldReviewPosts,
  submitFeedback as submitChatFeedback,
} from '@/services/chatService'
import { getOnboarding } from '@/services/onboardingService'
import { setRegenerationOption } from '@/services/regenerationFlowService'
import type { AIPostGeneration, ApiError, FeedbackPayload, PostWithImage } from '@/types/api'

const emptyFeedback: FeedbackPayload = {
  overallSatisfaction: 0,
  postsSatisfaction: 0,
  imagesSatisfaction: 0,
  suggestions: '',
}

export function useChatController() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const autoStartAttempted = useRef(false)
  const { toast } = useToast()

  const [loading, setLoading] = useState(true)
  const [generatingPosts, setGeneratingPosts] = useState(false)
  const [generatingImages, setGeneratingImages] = useState(false)
  const [postGen, setPostGen] = useState<AIPostGeneration | null>(null)
  const [postsWithImages, setPostsWithImages] = useState<PostWithImage[] | null>(null)

  const [showFeedbackSurvey, setShowFeedbackSurvey] = useState(false)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [feedbackData, setFeedbackData] = useState<FeedbackPayload>(emptyFeedback)

  const [showNewPostsOptions, setShowNewPostsOptions] = useState(false)
  const [showPostReview, setShowPostReview] = useState(false)
  const [showPostSelection, setShowPostSelection] = useState(false)
  const [selectedPosts, setSelectedPosts] = useState<number[]>([])
  const [regeneratingPosts, setRegeneratingPosts] = useState(false)

  useEffect(() => {
    const initChat = async () => {
      const fromOnboarding = (location.state as { postGenerationFromOnboarding?: AIPostGeneration })
        ?.postGenerationFromOnboarding

      try {
        const onboarding = await getOnboarding()
        if (!onboarding) {
          toast({
            title: t('common.onboardingRequired', 'Onboarding Required'),
            description: t(
              'chat.completeOnboardingFirst',
              'Please complete your onboarding profile to open the marketing chat.'
            ),
          })
          navigate('/new-onboarding')
          return
        }

        if (fromOnboarding) {
          setPostGen(fromOnboarding)
          if (shouldReviewPosts(fromOnboarding)) {
            setShowPostReview(true)
          }
          return
        }

        const data = await getPremiumPosts()
        if (data.post_generation) {
          setPostGen(data.post_generation)

          const gen = data.post_generation
          if (shouldReviewPosts(gen)) {
            setShowPostReview(true)
          }

          if (gen.images_status === 'processing') {
            setGeneratingImages(true)
          }

          if (gen.images_status === 'completed' && gen.has_images) {
            try {
              setPostsWithImages(mapLatestSessionImages(await getImagesHistory()))
            } catch (e) {
              console.error('Failed to reload images', e)
            }
          }
        }
      } catch (err) {
        console.error(err)
        toast({
          title: t('common.error', 'Error'),
          description: t(
            'chat.failedToLoad',
            'Failed to load chat data. Please refresh and try again.'
          ),
          variant: 'destructive',
        })
      } finally {
        setLoading(false)
      }
    }

    initChat()
  }, [navigate, toast, t, location.state])

  useEffect(() => {
    if (!postGen || postGen.images_status !== 'processing') {
      return
    }

    const pollInterval = setInterval(async () => {
      try {
        const data = await getPremiumPosts()
        if (data.post_generation) {
          const gen = data.post_generation
          setPostGen(gen)

          if (gen.images_status === 'completed' && gen.has_images) {
            setGeneratingImages(false)
            try {
              setPostsWithImages(mapLatestSessionImages(await getImagesHistory()))
            } catch (e) {
              console.error('Failed to reload images', e)
            }
            clearInterval(pollInterval)
          }

          if (gen.images_status === 'failed') {
            setGeneratingImages(false)
            clearInterval(pollInterval)
            toast({
              title: t('common.error', 'Error'),
              description: t(
                'chat.imageGenerationFailed',
                'Image generation failed. Please try again.'
              ),
              variant: 'destructive',
            })
          }
        }
      } catch (err) {
        console.error('Failed to poll generation status', err)
      }
    }, 3000)

    return () => clearInterval(pollInterval)
  }, [postGen, toast, t])

  const handleGeneratePosts = useCallback(
    async (force: boolean = false) => {
      setGeneratingPosts(true)
      try {
        const data = await generatePremiumPosts(force ? { force_regenerate: true } : undefined)

        if (data.post_generation) {
          setPostGen(data.post_generation)
          setPostsWithImages(null)
          toast({
            title: t('chat.generationSuccess', 'Campaign Formulated'),
            description: t(
              'chat.generationSuccessDesc',
              '5 marketing posts have been tailored to your business profile!'
            ),
          })
          setShowPostReview(true)
        }
      } catch (err) {
        const error = err as ApiError
        console.error(err)
        toast({
          title: t('common.error', 'Error'),
          description:
            error.response?.data?.error ||
            t('chat.failedToGenerate', 'Failed to generate posts. Please try again.'),
          variant: 'destructive',
        })
      } finally {
        setGeneratingPosts(false)
      }
    },
    [toast, t]
  )

  useEffect(() => {
    const state = location.state as {
      autoStartCampaign?: boolean
      forceRegenerate?: boolean
      postGenerationFromOnboarding?: unknown
    }
    const autoStart = Boolean(state?.autoStartCampaign)
    const forceRegenerate = Boolean(state?.forceRegenerate)
    const alreadyHasPosts = Boolean(state?.postGenerationFromOnboarding)

    if (!autoStart || autoStartAttempted.current || loading || generatingPosts) {
      return
    }

    if (!forceRegenerate && alreadyHasPosts) {
      return
    }

    const checkExistingAndGenerate = async () => {
      if (!forceRegenerate) {
        try {
          const data = await getPremiumPosts()
          if (data.post_generation) {
            setPostGen(data.post_generation)
            if (shouldReviewPosts(data.post_generation)) {
              setShowPostReview(true)
            }
            return
          }
        } catch (err) {
          console.error('Failed to check existing posts:', err)
        }
      }

      autoStartAttempted.current = true
      handleGeneratePosts(forceRegenerate)
    }

    checkExistingAndGenerate()
  }, [loading, postGen, generatingPosts, location.state, handleGeneratePosts])

  const handleGenerateImages = useCallback(async () => {
    if (!postGen) return
    setGeneratingImages(true)

    try {
      const data = await generateCampaignImages(postGen.id)
      setPostGen(data.post_generation)
      setPostsWithImages(data.posts_with_images)

      toast({
        title: t('chat.imagesReady', 'Visual Assets Prepared'),
        description: t(
          'chat.imagesReadyDesc',
          'Engaging visual designs have been attached to all your campaign posts!'
        ),
      })
    } catch (err) {
      const error = err as ApiError
      console.error(err)
      if (error.response?.status === 409) {
        toast({
          title: t('common.error', 'Generation in Progress'),
          description:
            error.response?.data?.error ||
            t(
              'chat.generationInProgress',
              'Image generation is already in progress. Please wait for it to complete.'
            ),
          variant: 'destructive',
        })
        return
      }
      toast({
        title: t('common.error', 'Error'),
        description:
          error.response?.data?.error ||
          t('chat.failedToGenerateImages', 'Failed to generate matching campaign visuals.'),
        variant: 'destructive',
      })
    } finally {
      if (postGen.images_status !== 'processing') {
        setGeneratingImages(false)
      }
    }
  }, [postGen, toast, t])

  const handleRegenerateSelectedPosts = useCallback(async () => {
    if (selectedPosts.length === 0) {
      toast({
        title: t('common.error', 'Error'),
        description: t('postReview.noSelection', 'Please select at least one post to regenerate.'),
        variant: 'destructive',
      })
      return
    }

    setRegeneratingPosts(true)
    try {
      const data = await regenerateSelectedPosts(selectedPosts)
      if (data.posts) {
        setPostGen(
          data.post_generation ?? {
            ...postGen,
            posts: data.posts,
            posts_review_complete: true,
          }
        )
        toast({
          title: t('postReview.regenerationSuccess', 'Posts regenerated successfully!'),
          description: '',
        })
        setShowPostReview(false)
        setShowPostSelection(false)
        setSelectedPosts([])
      }
    } catch (err) {
      const error = err as ApiError
      console.error(err)
      toast({
        title: t('common.error', 'Error'),
        description:
          error.response?.data?.error ||
          t('postReview.regenerationError', 'Failed to regenerate posts. Please try again.'),
        variant: 'destructive',
      })
    } finally {
      setRegeneratingPosts(false)
    }
  }, [postGen, selectedPosts, toast, t])

  const handlePostReviewNo = useCallback(async () => {
    try {
      const data = await completePostReview()
      if (data.post_generation) {
        setPostGen(data.post_generation)
      }
      setShowPostReview(false)
      setShowPostSelection(false)
    } catch (err) {
      const error = err as ApiError
      console.error(err)
      toast({
        title: t('common.error', 'Error'),
        description:
          error.response?.data?.error ||
          t('chat.failedToLoad', 'Failed to update workflow. Please try again.'),
        variant: 'destructive',
      })
    }
  }, [toast, t])

  const togglePostSelection = useCallback((index: number) => {
    setSelectedPosts((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    )
  }, [])

  const resetPostSelection = useCallback(() => {
    setShowPostSelection(false)
    setSelectedPosts([])
  }, [])

  const handleFeedbackSubmit = useCallback(async () => {
    try {
      await submitChatFeedback(feedbackData)
      setFeedbackSubmitted(true)
      setTimeout(() => {
        setShowFeedbackSurvey(false)
        setFeedbackSubmitted(false)
        setFeedbackData(emptyFeedback)
      }, 3000)
    } catch (err) {
      console.error(err)
      toast({
        title: t('common.error', 'Error'),
        description: t(
          'chat.failedToSubmitFeedback',
          'Failed to submit feedback. Please try again.'
        ),
        variant: 'destructive',
      })
    }
  }, [feedbackData, toast, t])

  const handleUseNewBusinessInfo = useCallback(() => {
    setShowNewPostsOptions(false)
    setRegenerationOption('new_business_info')
    navigate('/new-onboarding')
  }, [navigate])

  const handleUseExistingBusinessInfo = useCallback(() => {
    setShowNewPostsOptions(false)
    setRegenerationOption('existing_business_info')
    navigate('/pricing')
  }, [navigate])

  return {
    loading,
    generatingPosts,
    generatingImages,
    postGen,
    postsWithImages,
    showFeedbackSurvey,
    feedbackSubmitted,
    feedbackData,
    showNewPostsOptions,
    showPostReview,
    showPostSelection,
    selectedPosts,
    regeneratingPosts,
    setFeedbackData,
    setShowFeedbackSurvey,
    setShowNewPostsOptions,
    setShowPostSelection,
    handleGeneratePosts,
    handleGenerateImages,
    handleRegenerateSelectedPosts,
    handlePostReviewYes: () => setShowPostSelection(true),
    handlePostReviewNo,
    togglePostSelection,
    resetPostSelection,
    handleFeedbackSubmit,
    handleUseNewBusinessInfo,
    handleUseExistingBusinessInfo,
  }
}
