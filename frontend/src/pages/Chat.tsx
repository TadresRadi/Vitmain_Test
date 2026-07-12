import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Loader2,
  Sparkles,
  Image as ImageIcon,
  X,
  Star,
  RefreshCw,
  FileText
} from "lucide-react"
import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import DashboardLayout from "@/components/DashboardLayout"
import { useToast } from "@/hooks/use-toast"
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
} from "@/services/chatService"
import { getOnboarding } from "@/services/onboardingService"
import { setRegenerationOption, getRegenerationOption, clearRegenerationOption } from "@/services/regenerationFlowService"
import type { AIPostGeneration, ApiError, FeedbackPayload, PostWithImage } from "@/types/api"

export default function Chat() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const autoStartAttempted = useRef(false)
  const { toast } = useToast()
  
  const [loading, setLoading] = useState(true)
  const [generatingPosts, setGeneratingPosts] = useState(false)
  const [generatingImages, setGeneratingImages] = useState(false)

  // Active post generation state from backend
  const [postGen, setPostGen] = useState<AIPostGeneration | null>(null)
  
  // Posts with images after image generation: { post_index: number, text: string, image_url: string }[]
  const [postsWithImages, setPostsWithImages] = useState<PostWithImage[] | null>(null)

  // Feedback survey state
  const [showFeedbackSurvey, setShowFeedbackSurvey] = useState(false)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [feedbackData, setFeedbackData] = useState<FeedbackPayload>({
    overallSatisfaction: 0,
    postsSatisfaction: 0,
    imagesSatisfaction: 0,
    suggestions: ""
  })

  // Generate new posts options state
  const [showNewPostsOptions, setShowNewPostsOptions] = useState(false)

  // Post review state
  const [showPostReview, setShowPostReview] = useState(false)
  const [showPostSelection, setShowPostSelection] = useState(false)
  const [selectedPosts, setSelectedPosts] = useState<number[]>([])
  const [regeneratingPosts, setRegeneratingPosts] = useState(false)

  // Load post generation state on mount
  useEffect(() => {
    const initChat = async () => {
      const fromOnboarding = (location.state as { postGenerationFromOnboarding?: AIPostGeneration })
        ?.postGenerationFromOnboarding

      try {
        const onboarding = await getOnboarding()
        if (!onboarding) {
          toast({
            title: t("common.onboardingRequired", "Onboarding Required"),
            description: t("chat.completeOnboardingFirst", "Please complete your onboarding profile to open the marketing chat."),
          })
          navigate("/new-onboarding")
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

          // Check if image generation is currently in progress
          if (gen.images_status === 'processing') {
            setGeneratingImages(true)
          }

          // If images are completed, fetch them from the latest generation session
          if (gen.images_status === 'completed' && gen.has_images) {
            try {
              setPostsWithImages(mapLatestSessionImages(await getImagesHistory()))
            } catch (e) {
              console.error("Failed to reload images", e)
            }
          }
        }
      } catch (err) {
        console.error(err)
        toast({
          title: t("common.error", "Error"),
          description: t("chat.failedToLoad", "Failed to load chat data. Please refresh and try again."),
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }
    
    initChat()
  }, [navigate, toast, t, location.state])

  // Poll for image generation status when processing
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

          // If generation completed, fetch images and stop polling
          if (gen.images_status === 'completed' && gen.has_images) {
            setGeneratingImages(false)
            try {
              setPostsWithImages(mapLatestSessionImages(await getImagesHistory()))
            } catch (e) {
              console.error("Failed to reload images", e)
            }
            clearInterval(pollInterval)
          }

          // If generation failed, stop polling
          if (gen.images_status === 'failed') {
            setGeneratingImages(false)
            clearInterval(pollInterval)
            toast({
              title: t("common.error", "Error"),
              description: t("chat.imageGenerationFailed", "Image generation failed. Please try again."),
              variant: "destructive",
            })
          }
        }
      } catch (err) {
        console.error("Failed to poll generation status", err)
      }
    }, 3000) // Poll every 3 seconds

    return () => clearInterval(pollInterval)
  }, [postGen, toast, t])

  // Handle Initial Post Generation
  const handleGeneratePosts = async () => {
    setGeneratingPosts(true)
    try {
      // Check if this is a regeneration flow
      const regenerationOption = getRegenerationOption()
      const forceRegenerate = regenerationOption !== null
      
      const data = await generatePremiumPosts(forceRegenerate ? { force_regenerate: true } : undefined)
      
      // Clear regeneration option after successful generation
      if (regenerationOption) {
        clearRegenerationOption()
      }
      
      if (data.post_generation) {
        setPostGen(data.post_generation)
        toast({
          title: t("chat.generationSuccess", "Campaign Formulated"),
          description: t("chat.generationSuccessDesc", "5 marketing posts have been tailored to your business profile!"),
        })
        // Show post review after generation
        setShowPostReview(true)
      }
    } catch (err) {
      const error = err as ApiError
      console.error(err)
      toast({
        title: t("common.error", "Error"),
        description: error.response?.data?.error || t("chat.failedToGenerate", "Failed to generate posts. Please try again."),
        variant: "destructive",
      })
    } finally {
      setGeneratingPosts(false)
    }
  }

  // Auto-start only when posts were not already generated during onboarding
  useEffect(() => {
    const state = location.state as {
      autoStartCampaign?: boolean
      postGenerationFromOnboarding?: unknown
    }
    const autoStart = Boolean(state?.autoStartCampaign)
    const alreadyHasPosts = Boolean(state?.postGenerationFromOnboarding)
    
    // Only auto-start if:
    // - autoStart is true
    // - posts don't already exist from onboarding
    // - no auto-start attempt has been made
    // - loading is complete
    // - no posts are currently loaded
    // - not currently generating
    // - AND no existing post generation is in progress (check via API)
    if (
      autoStart &&
      !alreadyHasPosts &&
      !autoStartAttempted.current &&
      !loading &&
      postGen === null &&
      !generatingPosts
    ) {
      // Check if user already has posts in the database before auto-starting
      const checkExistingPosts = async () => {
        try {
          const data = await getPremiumPosts()
          if (data.post_generation) {
            // Posts already exist, load them instead of regenerating
            setPostGen(data.post_generation)
            if (shouldReviewPosts(data.post_generation)) {
              setShowPostReview(true)
            }
            return
          }
          // No posts exist, safe to auto-start
          autoStartAttempted.current = true
          handleGeneratePosts()
        } catch (err) {
          console.error("Failed to check existing posts:", err)
          // On error, proceed with auto-start
          autoStartAttempted.current = true
          handleGeneratePosts()
        }
      }
      
      checkExistingPosts()
    }
  }, [loading, postGen, generatingPosts, location.state])

  // Generate visuals (Unsplash images mapped to posts)
  const handleGenerateImages = async () => {
    if (!postGen) return
    setGeneratingImages(true)

    try {
      const data = await generateCampaignImages(postGen.id)
      setPostGen(data.post_generation)
      setPostsWithImages(data.posts_with_images)

      toast({
        title: t("chat.imagesReady", "Visual Assets Prepared"),
        description: t("chat.imagesReadyDesc", "Engaging visual designs have been attached to all your campaign posts!"),
      })
    } catch (err) {
      const error = err as ApiError
      console.error(err)
      // Handle 409 Conflict - generation already in progress
      if (error.response?.status === 409) {
        toast({
          title: t("common.error", "Generation in Progress"),
          description: error.response?.data?.error || t("chat.generationInProgress", "Image generation is already in progress. Please wait for it to complete."),
          variant: "destructive",
        })
        // Keep generatingImages true to reflect the ongoing generation
        return
      }
      toast({
        title: t("common.error", "Error"),
        description: error.response?.data?.error || t("chat.failedToGenerateImages", "Failed to generate matching campaign visuals."),
        variant: "destructive",
      })
    } finally {
      // Only set generatingImages to false if generation is not processing
      if (postGen.images_status !== 'processing') {
        setGeneratingImages(false)
      }
    }
  }

  // Handle regenerating selected posts
  const handleRegenerateSelectedPosts = async () => {
    if (selectedPosts.length === 0) {
      toast({
        title: t("common.error", "Error"),
        description: t("postReview.noSelection", "Please select at least one post to regenerate."),
        variant: "destructive",
      })
      return
    }

    setRegeneratingPosts(true)
    try {
      const data = await regenerateSelectedPosts(selectedPosts)
      if (data.posts) {
        setPostGen(data.post_generation ?? {
          ...postGen,
          posts: data.posts,
          posts_review_complete: true,
        })
        toast({
          title: t("postReview.regenerationSuccess", "Posts regenerated successfully!"),
          description: "",
        })
        setShowPostReview(false)
        setShowPostSelection(false)
        setSelectedPosts([])
      }
    } catch (err) {
      const error = err as ApiError
      console.error(err)
      toast({
        title: t("common.error", "Error"),
        description: error.response?.data?.error || t("postReview.regenerationError", "Failed to regenerate posts. Please try again."),
        variant: "destructive",
      })
    } finally {
      setRegeneratingPosts(false)
    }
  }

  // Handle Yes button - show post selection
  const handlePostReviewYes = () => {
    setShowPostSelection(true)
  }

  // Handle No button - confirm posts without regeneration
  const handlePostReviewNo = async () => {
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
        title: t("common.error", "Error"),
        description: error.response?.data?.error || t("chat.failedToLoad", "Failed to update workflow. Please try again."),
        variant: "destructive",
      })
    }
  }

  // Toggle post selection
  const togglePostSelection = (index: number) => {
    setSelectedPosts(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    )
  }

  // Handle feedback survey submission
  const handleFeedbackSubmit = async () => {
    try {
      await submitChatFeedback(feedbackData)
      setFeedbackSubmitted(true)
      setTimeout(() => {
        setShowFeedbackSurvey(false)
        setFeedbackSubmitted(false)
        setFeedbackData({
          overallSatisfaction: 0,
          postsSatisfaction: 0,
          imagesSatisfaction: 0,
          suggestions: ""
        })
      }, 3000)
    } catch (err) {
      console.error(err)
      toast({
        title: t("common.error", "Error"),
        description: t("chat.failedToSubmitFeedback", "Failed to submit feedback. Please try again."),
        variant: "destructive",
      })
    }
  }

  // Handle Option A: Use New Business Information
  const handleUseNewBusinessInfo = () => {
    setShowNewPostsOptions(false)
    setRegenerationOption("new_business_info")
    navigate("/new-onboarding")
  }

  // Handle Option B: Use Existing Business Information
  const handleUseExistingBusinessInfo = () => {
    setShowNewPostsOptions(false)
    setRegenerationOption("existing_business_info")
    navigate("/pricing")
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <div className="glass-dark border-b border-white/10 p-4 bg-black/40 backdrop-blur-md">
          <div className="max-w-7xl mx-auto flex items-center">
            <div className="flex items-center gap-3">
              <div>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-vitamin-base animate-pulse" />
                  {t("chat.title", "Vitamin AI Premium Marketing Strategist")}
                </h1>
                <p className="text-xs text-white/50">{t("chat.activeAssistance", "Formulate high-conversion copy campaigns")}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Campaign Studio - Main Content */}
        <div className="flex-grow flex overflow-hidden max-w-7xl w-full mx-auto p-4">
          
          {/* Campaign Studio Panel */}
          <div className="flex-1 flex flex-col glass-dark border border-white/10 rounded-2xl overflow-hidden bg-black/25 backdrop-blur-md">
            
            {/* Header */}
            <div className="p-4 border-b border-white/10 bg-white/5 flex items-center justify-between">
              <div>
                <h2 className="font-bold text-white flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-vitamin-base" />
                  {t("chat.campaignStudio", "Campaign Studio")}
                </h2>
                <p className="text-xs text-white/50">{t("chat.studioDesc", "Review and attach visual media assets")}</p>
              </div>
            </div>

            {/* Content Scroll Area */}
            <div className="flex-grow overflow-y-auto p-4 space-y-4">
              {loading ? (
                <div className="h-full flex flex-col items-center justify-center text-white/40 gap-2">
                  <Loader2 className="h-6 w-6 animate-spin text-vitamin-base" />
                  <p className="text-xs">{t("chat.connectingStudio", "Syncing Campaign Studio...")}</p>
                </div>
              ) : postGen === null ? (
                /* WELCOME / GENERATE CTA SCREEN */
                <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-6">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-vitamin-base to-pink-500 flex items-center justify-center shadow-lg shadow-vitamin-base/25">
                    <Sparkles className="h-8 w-8 text-white animate-pulse" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-bold text-white">{t("chat.formulatePrompt", "Formulate Premium Campaigns")}</h3>
                    <p className="text-xs text-white/60 leading-relaxed max-w-sm">
                      {t("chat.formulatePromptDesc", "Leverage Gemini Pro to construct exactly 5 comprehensive marketing posts translated into your profile language.")}
                    </p>
                  </div>
                  <Button 
                    onClick={handleGeneratePosts}
                    disabled={generatingPosts}
                    className="w-full bg-gradient-to-r from-vitamin-base to-pink-600 hover:from-vitamin-700 hover:to-pink-700 text-white font-medium h-12 rounded-xl flex items-center justify-center gap-2 shadow-lg"
                  >
                    {generatingPosts ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {t("chat.formulating", "Formulating Campaign...")}
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        {t("chat.generatePosts", "Formulate 5 Campaign Posts")}
                      </>
                    )}
                  </Button>
                </div>
              ) : (
                <>
                {/* POSTS LISTING */}
                <div className="space-y-4">
                  {postGen.posts.map((post: string, idx: number) => {
                    const imageObj = postsWithImages?.find(p => p.post_index === idx)
                    
                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.05 }}
                      >
                        <Card className="overflow-hidden glass-dark border border-white/10 transition-all duration-200 bg-black/40">
                          {/* Image Attachment (If Generated) */}
                          {imageObj?.image_url && (
                            <div className="relative aspect-video w-full overflow-hidden border-b border-white/10">
                              <img 
                                src={imageObj.image_url} 
                                alt={`Post #${idx + 1} Visual`} 
                                className="w-full h-full object-cover brightness-95 hover:scale-105 transition-transform duration-500"
                              />
                              <div className="absolute top-2 left-2 bg-black/75 px-2 py-0.5 rounded text-[10px] text-vitamin-400 font-bold border border-vitamin-500/20 uppercase tracking-wider">
                                {t("chat.visualMock", "Visual Asset Mock")}
                              </div>
                            </div>
                          )}
                          
                          <div className="p-4 space-y-3">
                            <div className="flex items-center justify-between">
                              <Badge variant="outline" className="text-white/40 border-white/15">
                                {`Post #${idx + 1}`}
                              </Badge>
                            </div>

                            <p className="text-sm text-white/80 leading-relaxed font-sans select-all whitespace-pre-line">
                              {post}
                            </p>
                          </div>
                        </Card>
                      </motion.div>
                    )
                  })}
                </div>

                {/* Inline Post Review Flow */}
                {showPostReview && !showPostSelection && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-4 rounded-xl border border-vitamin-500/25 bg-vitamin-base/5 space-y-4"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-vitamin-base/15 text-vitamin-base shrink-0">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{t("postReview.title", "Review Your Posts")}</h4>
                        <p className="text-xs text-white/60 mt-1">{t("postReview.message", "Do you want to modify any of these posts?")}</p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <Button
                        onClick={handlePostReviewYes}
                        className="flex-1 bg-vitamin-base hover:bg-vitamin-700 text-white font-medium h-10 rounded-lg"
                      >
                        {t("postReview.yes", "Yes")}
                      </Button>
                      <Button
                        onClick={handlePostReviewNo}
                        variant="outline"
                        className="flex-1 border-white/20 text-black dark:text-white hover:bg-vitamin-base/10 dark:hover:bg-white/10 hover:text-black dark:hover:text-white h-10 rounded-lg"
                      >
                        {t("postReview.no", "No")}
                      </Button>
                    </div>
                  </motion.div>
                )}

                {/* Generate Images prompt — only after post review is complete and not currently processing */}
                {postGen.posts_review_complete && !postGen.has_images && postGen.images_status !== 'processing' && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-4 rounded-xl border border-vitamin-500/25 bg-vitamin-base/5 space-y-4"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-vitamin-base/15 text-vitamin-base shrink-0">
                        <ImageIcon className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{t("postReview.generateImagesTitle", "Generate Images")}</h4>
                        <p className="text-xs text-white/60 mt-1">{t("postReview.generateImagesDesc", "Your posts are ready. Generate matching visuals for all 5 campaign posts.")}</p>
                      </div>
                    </div>

                    <Button
                      onClick={handleGenerateImages}
                      disabled={generatingImages}
                      className="w-full bg-gradient-to-r from-vitamin-base to-pink-500 hover:from-vitamin-700 hover:to-pink-600 text-white font-semibold text-xs h-10 rounded-lg flex items-center justify-center gap-2 shadow-md"
                    >
                      {generatingImages ? (
                        <>
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          {t("chat.attachingVisuals", "Attaching Visuals...")}
                        </>
                      ) : (
                        <>
                          <Sparkles className="h-3.5 w-3.5 text-white" />
                          {t("postReview.generateImages", "Generate Images")}
                        </>
                      )}
                    </Button>
                  </motion.div>
                )}

                {/* Show generation in progress message */}
                {postGen.images_status === 'processing' && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-4 rounded-xl border border-vitamin-500/25 bg-vitamin-base/5 space-y-4"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-vitamin-base/15 text-vitamin-base shrink-0">
                        <Loader2 className="w-5 h-5 animate-spin" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{t("chat.generatingImages", "Generating Images")}</h4>
                        <p className="text-xs text-white/60 mt-1">{t("chat.generatingImagesDesc", "Your visual assets are being generated. This may take a moment.")}</p>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Inline Post Selection Flow */}
                {showPostSelection && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-4 rounded-xl border border-vitamin-500/25 bg-vitamin-base/5 space-y-4"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-vitamin-base/15 text-vitamin-base shrink-0">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{t("postReview.title", "Review Your Posts")}</h4>
                        <p className="text-xs text-white/60 mt-1">{t("postReview.selectPosts", "Select the post numbers you would like to modify.")}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-5 gap-2">
                      {Array.from({ length: 5 }, (_, i) => (
                        <button
                          key={i}
                          onClick={() => togglePostSelection(i)}
                          className={`p-3 rounded-lg border-2 transition-all ${
                            selectedPosts.includes(i)
                              ? 'bg-vitamin-base border-vitamin-base text-white'
                              : 'bg-white/5 border-white/20 text-white/60 hover:border-white/40'
                          }`}
                        >
                          {`Post ${i + 1}`}
                        </button>
                      ))}
                    </div>

                    <div className="flex gap-3">
                      <Button
                        onClick={handleRegenerateSelectedPosts}
                        disabled={regeneratingPosts || selectedPosts.length === 0}
                        className="flex-1 bg-vitamin-base hover:bg-vitamin-700 text-white font-medium h-10 rounded-lg"
                      >
                        {regeneratingPosts ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                            {t("postReview.regenerating", "Regenerating...")}
                          </>
                        ) : (
                          t("postReview.done", "Done")
                        )}
                      </Button>
                      <Button
                        onClick={() => {
                          setShowPostSelection(false)
                          setSelectedPosts([])
                        }}
                        variant="outline"
                        className="px-4 border-white/20 text-white hover:bg-white/10 h-10 rounded-lg"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </motion.div>
                )}
                </>
              )}
            </div>

            {/* Bottom Actions Suite */}
            {postGen && (
              <div className="p-4 border-t border-white/10 bg-black/45 space-y-3 backdrop-blur-md">
                
                {/* Post-Generation Options */}
                {postGen.has_images && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-3"
                  >
                    {/* Feedback Survey Option */}
                    <Button
                      onClick={() => setShowFeedbackSurvey(true)}
                      variant="outline"
                      className="w-full border-white/20 text-black dark:text-white hover:bg-white/10 h-10 rounded-lg flex items-center justify-center gap-2"
                    >
                      <Star className="h-4 w-4" />
                      {t("chat.feedbackSurvey", "Feedback Survey")}
                    </Button>

                    {/* Generate New Posts Option */}
                    <Button
                      onClick={() => setShowNewPostsOptions(true)}
                      variant="outline"
                      className="w-full border-vitamin-base/30 text-vitamin-base hover:bg-vitamin-base/10 h-10 rounded-lg flex items-center justify-center gap-2"
                    >
                      <RefreshCw className="h-4 w-4" />
                      {t("chat.generateNewPosts", "Generate New Posts and Images")}
                    </Button>
                  </motion.div>
                )}

              </div>
            )}

          </div>

        </div>

        {/* Feedback Survey Modal */}
        <AnimatePresence>
          {showFeedbackSurvey && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="glass-dark border border-white/20 rounded-2xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <Star className="h-5 w-5 text-vitamin-base" />
                    {t("chat.feedbackSurvey", "Feedback Survey")}
                  </h3>
                  <button
                    onClick={() => setShowFeedbackSurvey(false)}
                    className="text-white/60 hover:text-white transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                {feedbackSubmitted ? (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Star className="h-8 w-8 text-green-400" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-2">{t("chat.feedbackSubmitted", "Thank you for your feedback!")}</h4>
                    <p className="text-sm text-white/60">{t("chat.feedbackSubmittedDesc", "Your responses have been recorded. We appreciate your input.")}</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <p className="text-sm text-white/60">{t("chat.feedbackSurveyDesc", "Help us improve our service by sharing your experience.")}</p>

                    {/* Overall Satisfaction */}
                    <div>
                      <label className="block text-sm font-medium text-white mb-3">{t("chat.overallSatisfaction", "Rate your overall satisfaction with the service from 1 to 10.")}</label>
                      <div className="flex gap-2">
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
                          <button
                            key={rating}
                            onClick={() => setFeedbackData(prev => ({ ...prev, overallSatisfaction: rating }))}
                            className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
                              feedbackData.overallSatisfaction === rating
                                ? 'bg-vitamin-base text-white'
                                : 'bg-white/10 text-white/60 hover:bg-white/20'
                            }`}
                          >
                            {rating}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Posts Satisfaction */}
                    <div>
                      <label className="block text-sm font-medium text-white mb-3">{t("chat.postsSatisfaction", "Rate your satisfaction with the generated posts from 1 to 10.")}</label>
                      <div className="flex gap-2">
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
                          <button
                            key={rating}
                            onClick={() => setFeedbackData(prev => ({ ...prev, postsSatisfaction: rating }))}
                            className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
                              feedbackData.postsSatisfaction === rating
                                ? 'bg-vitamin-base text-white'
                                : 'bg-white/10 text-white/60 hover:bg-white/20'
                            }`}
                          >
                            {rating}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Images Satisfaction */}
                    <div>
                      <label className="block text-sm font-medium text-white mb-3">{t("chat.imagesSatisfaction", "Rate your satisfaction with the generated images and image quality from 1 to 10.")}</label>
                      <div className="flex gap-2">
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
                          <button
                            key={rating}
                            onClick={() => setFeedbackData(prev => ({ ...prev, imagesSatisfaction: rating }))}
                            className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
                              feedbackData.imagesSatisfaction === rating
                                ? 'bg-vitamin-base text-white'
                                : 'bg-white/10 text-white/60 hover:bg-white/20'
                            }`}
                          >
                            {rating}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Suggestions */}
                    <div>
                      <label className="block text-sm font-medium text-white mb-3">{t("chat.suggestions", "Do you have any suggestions, improvements, or features you would like to see added to the website?")}</label>
                      <textarea
                        value={feedbackData.suggestions}
                        onChange={(e) => setFeedbackData(prev => ({ ...prev, suggestions: e.target.value }))}
                        rows={4}
                        className="w-full bg-white/10 border border-white/20 text-white placeholder-white/40 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-vitamin-base resize-none"
                        placeholder={t("chat.suggestionsPlaceholder", "Share your thoughts...")}
                      />
                    </div>

                    <Button
                      onClick={handleFeedbackSubmit}
                      disabled={feedbackData.overallSatisfaction === 0 || feedbackData.postsSatisfaction === 0 || feedbackData.imagesSatisfaction === 0}
                      className="w-full bg-vitamin-base hover:bg-vitamin-700 text-white font-medium h-11 rounded-xl"
                    >
                      {t("chat.submitFeedback", "Submit Feedback")}
                    </Button>
                  </div>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Generate New Posts Options Modal */}
        <AnimatePresence>
          {showNewPostsOptions && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="glass-dark border border-white/20 rounded-2xl p-6 max-w-md w-full"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <RefreshCw className="h-5 w-5 text-vitamin-base" />
                    {t("chat.generateNewPosts", "Generate New Posts and Images")}
                  </h3>
                  <button
                    onClick={() => setShowNewPostsOptions(false)}
                    className="text-white/60 hover:text-white transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <p className="text-sm text-white/60 mb-6">{t("chat.generateNewPostsDesc", "Create a fresh set of marketing content for your business.")}</p>

                <div className="space-y-4">
                  {/* Option A: Use New Business Information */}
                  <Card className="glass-dark border border-white/20 p-4 hover:border-vitamin-base/50 transition-colors cursor-pointer" onClick={handleUseNewBusinessInfo}>
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-vitamin-base/15 text-vitamin-base shrink-0">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white mb-1">{t("chat.useNewBusinessInfo", "Use New Business Information")}</h4>
                        <p className="text-xs text-white/60">{t("chat.useNewBusinessInfoDesc", "Provide new business details to generate completely different content.")}</p>
                      </div>
                    </div>
                  </Card>

                  {/* Option B: Use Existing Business Information */}
                  <Card className="glass-dark border border-white/20 p-4 hover:border-vitamin-base/50 transition-colors cursor-pointer" onClick={handleUseExistingBusinessInfo}>
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-vitamin-base/15 text-vitamin-base shrink-0">
                        <RefreshCw className="h-5 w-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white mb-1">{t("chat.useExistingBusinessInfo", "Use Existing Business Information")}</h4>
                        <p className="text-xs text-white/60">{t("chat.useExistingBusinessInfoDesc", "Regenerate content using your current business profile.")}</p>
                      </div>
                    </div>
                  </Card>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </DashboardLayout>
  )
}
