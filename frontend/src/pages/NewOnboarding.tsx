import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { ArrowRight, ArrowLeft, Loader2, Check } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import AnimatedBackground from "@/components/AnimatedBackground"

import { useToast } from "@/hooks/use-toast"
import { saveOnboarding, type OnboardingFormData } from "@/services/onboardingService"
import { clearRegenerationOption, getRegenerationOption } from "@/services/regenerationFlowService"
import type { ApiError } from "@/types/api"

export default function NewOnboarding() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const { toast } = useToast()

  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Partial<OnboardingFormData>>({
    marketingGoals: []
  })
  const [currentAnswer, setCurrentAnswer] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showOtherInput, setShowOtherInput] = useState(false)
  const [selectedMarketingGoals, setSelectedMarketingGoals] = useState<string[]>([])

  // Business type categories with their subcategories
  const businessTypeCategories = {
    restaurant: {
      subcategories: ["grills", "shawarma", "pizza", "seafood", "syrianCuisine", "burgers", "koshari", "desserts", "other"]
    },
    cafe: {
      subcategories: ["coffee", "desserts", "beverages", "lounge"]
    },
    clinic: {
      subcategories: ["dental", "pediatrics", "dermatology", "obstetricsGynecology", "orthopedics", "internalMedicine", "ent", "clinicalNutrition", "other"]
    },
    pharmacy: {
      subcategories: []
    },
    laboratory: {
      subcategories: []
    },
    radiologyCenter: {
      subcategories: []
    },
    store: {
      subcategories: ["onlineStore", "clothing", "electronics", "perfumes", "mobilePhones", "kidsProducts", "homeSupplies", "other"]
    },
    clothing: {
      subcategories: ["mensFashion", "womensFashion", "kidsClothing", "sportswear", "modestFashion"]
    },
    company: {
      subcategories: ["marketing", "softwareDevelopment", "construction", "tourism", "shippingLogistics", "cleaningServices", "other"]
    },
    engineeringOffice: {
      subcategories: []
    },
    gym: {
      subcategories: []
    },
    other: {
      subcategories: []
    }
  }

  const marketingGoalOptions = ["sales", "brandAwareness", "bookings", "messages"]
  const targetAudienceOptions = ["youth", "women", "families", "men", "everyone", "other"]
  const toneOfVoiceOptions = ["humorous", "professional", "premium", "youthful", "medical", "trendy", "other"]

  // Dynamic questions based on business type selection
  const getQuestions = () => {
    const baseQuestions = [
      {
        id: 'businessName',
        type: 'text'
      },
      {
        id: 'governorate',
        type: 'text'
      },
      {
        id: 'businessType',
        type: 'select',
        options: Object.keys(businessTypeCategories)
      }
    ]

    // Add subcategory question only if business type has subcategories
    if (answers.businessType && businessTypeCategories[answers.businessType as keyof typeof businessTypeCategories]?.subcategories.length > 0) {
      baseQuestions.push({
        id: 'businessSubtype',
        type: 'select',
        options: businessTypeCategories[answers.businessType as keyof typeof businessTypeCategories]?.subcategories || []
      })
    }

    baseQuestions.push(
      {
        id: 'marketingGoals',
        type: 'multi-select',
        options: marketingGoalOptions
      },
      {
        id: 'targetAudience',
        type: 'select',
        options: targetAudienceOptions
      },
      {
        id: 'toneOfVoice',
        type: 'select',
        options: toneOfVoiceOptions
      }
    )

    return baseQuestions
  }

  const questions = getQuestions()

const handleNext = () => {
  const question = questions[currentQuestion]

  if (!question) return

  if (question.type === "select" && checkIfOther(currentAnswer)) {
    setShowOtherInput(true)
    setCurrentAnswer("")
    return
  }

  if (!currentAnswer.trim()) return

  const nextAnswers = {
    ...answers,
    [question.id]: currentAnswer,
  }

  setAnswers(nextAnswers)

  if (question.id === "businessType") {
    const subcategories =
      businessTypeCategories[
        currentAnswer as keyof typeof businessTypeCategories
      ]?.subcategories ?? []

    setCurrentQuestion((previous) => previous + 1)
    setCurrentAnswer("")
    setShowOtherInput(false)

    // The dynamically computed list automatically includes or excludes
    // the subtype question on the next render.
    if (subcategories.length === 0) {
      setAnswers({
        ...nextAnswers,
        businessSubtype: "",
      })
    }

    return
  }

  if (currentQuestion < questions.length - 1) {
    setCurrentQuestion((previous) => previous + 1)
    setCurrentAnswer("")
    setShowOtherInput(false)
    return
  }

  void completeOnboarding(nextAnswers as OnboardingFormData)
}


  const handleMultiSelectNext = () => {
    const nextAnswers = {
      ...answers,
      marketingGoals: selectedMarketingGoals
    }
    
    setAnswers(nextAnswers)
    
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1)
      setCurrentAnswer("")
      setShowOtherInput(false)
    } else {
      void completeOnboarding(nextAnswers as OnboardingFormData)
    }
  }

  const completeOnboarding = async (finalAnswers: OnboardingFormData) => {
    setIsSubmitting(true)
    try {
      await saveOnboardingData(finalAnswers)

      toast({
        title: t("onboarding.new.savedTitle", "Profile saved"),
        description: t("onboarding.new.savedDesc", "Next, choose a plan to unlock your campaign posts."),
      })

      // Check if this is a regeneration flow
      const isRegenerationFlow = getRegenerationOption() === "new_business_info"

      // Go to pricing; post generation must happen only after plan selection.
      // For regeneration flow, we want to pass state to indicate this is for regeneration
      navigate("/pricing", { 
        replace: true,
        state: { 
          isRegenerationFlow: isRegenerationFlow 
        }
      })
    } catch (error) {
      const apiError = error as ApiError
      console.error("Onboarding completion failed:", error)
      toast({
        title: t("common.error", "Error"),
        description:
          apiError.response?.data?.error ||
          t("onboarding.new.saveFailed", "Could not save onboarding. Please try again."),
        variant: "destructive",
      })
      setIsSubmitting(false)
    }
  }

const handleOtherSubmit = () => {
  const value = currentAnswer.trim()
  if (!value) return

  const question = questions[currentQuestion]
  if (!question) return

  let nextAnswers: Partial<OnboardingFormData> = {
    ...answers,
  }

  if (question.id === "businessType") {
    nextAnswers = {
      ...nextAnswers,
      businessType: "other",
      businessTypeOther: value,
      businessSubtype: "",
    }
  } else if (question.id === "businessSubtype") {
    nextAnswers = {
      ...nextAnswers,
      businessSubtype: "other",
      businessTypeOther: value,
    }
  } else if (question.id === "targetAudience") {
    nextAnswers = {
      ...nextAnswers,
      targetAudience: "other",
      targetAudienceOther: value,
    }
  } else if (question.id === "toneOfVoice") {
    nextAnswers = {
      ...nextAnswers,
      toneOfVoice: "other",
      toneOfVoiceOther: value,
    }
  }

  setAnswers(nextAnswers)
  setShowOtherInput(false)
  setCurrentAnswer("")
  setCurrentQuestion((previous) => previous + 1)
}


  const checkIfOther = (value: string) => {
    return value === "other"
  }

  const saveOnboardingData = async (finalAnswers: OnboardingFormData) => {
    const isRegenerationFlow = getRegenerationOption() === "new_business_info"
    const response = await saveOnboarding({
      data: finalAnswers,
      createNew: isRegenerationFlow,
    })

    if (isRegenerationFlow) {
      clearRegenerationOption()
    }

    return response
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      const newQuestions = getQuestions()
      
      // If we're on marketing goals question and the previous question would have been subcategory that was skipped, go back to business type
      if (questions[currentQuestion].id === 'marketingGoals') {
        const hasSubcategories = answers.businessType && businessTypeCategories[answers.businessType as keyof typeof businessTypeCategories]?.subcategories.length > 0
        if (!hasSubcategories) {
          // Skip back to business type
          const businessTypeIndex = newQuestions.findIndex(q => q.id === 'businessType')
          setCurrentQuestion(businessTypeIndex)
          setCurrentAnswer(answers.businessType as string || "")
          setShowOtherInput(false)
          return
        }
      }
      
      setCurrentQuestion(prev => prev - 1)
      const prevQuestion = newQuestions[currentQuestion - 1]
      if (prevQuestion.id === 'marketingGoals') {
        setCurrentAnswer("")
      } else {
        setCurrentAnswer(answers[prevQuestion.id as keyof OnboardingFormData] as string || "")
      }
      setShowOtherInput(false)
    }
  }

  const toggleMarketingGoal = (goal: string) => {
    setSelectedMarketingGoals(prev => {
      if (prev.includes(goal)) {
        return prev.filter(g => g !== goal)
      } else {
        return [...prev, goal]
      }
    })
  }

  if (isSubmitting) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        <AnimatedBackground />
        <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 text-center">
          <Loader2 className="h-12 w-12 text-vitamin-base animate-spin mb-6" />
          <h2 className="text-2xl font-bold text-white mb-2">
            {t("onboarding.new.saving", "Saving your profile...")}
          </h2>
          <p className="text-white/60 max-w-md">
            {t("onboarding.new.savingDesc", "Your answers are being saved. You'll pick a plan next.")}
          </p>
        </div>
      </div>
    )
  }


  return (
    <div className="min-h-screen relative overflow-hidden">
      <AnimatedBackground />
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-2xl"
        >
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-white/60 text-sm mb-2">
              <span>{t("onboarding.new.questionOf", { current: currentQuestion + 1, total: questions.length })}</span>
              <span>{Math.round(((currentQuestion + 1) / questions.length) * 100)}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2">
              <motion.div
                className="bg-vitamin-base h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>

          {/* Question Card */}
          <Card className="glass-dark border border-white/20 p-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentQuestion}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="text-3xl font-bold text-white mb-8">
                  {questions[currentQuestion].id === 'businessName' && t('onboarding.new.businessName')}
                  {questions[currentQuestion].id === 'governorate' && t('onboarding.new.governorate')}
                  {questions[currentQuestion].id === 'businessType' && t('onboarding.new.businessType')}
                  {questions[currentQuestion].id === 'businessSubtype' && t('onboarding.new.businessSubtype')}
                  {questions[currentQuestion].id === 'marketingGoals' && t('onboarding.new.marketingGoalsLabel')}
                  {questions[currentQuestion].id === 'targetAudience' && t('onboarding.new.targetAudience')}
                  {questions[currentQuestion].id === 'toneOfVoice' && t('onboarding.new.toneOfVoice')}
                </h2>
                
                {showOtherInput ? (
                  <div className="space-y-4">
                    <Input
                      value={currentAnswer}
                      onChange={(e) => setCurrentAnswer(e.target.value)}
                      placeholder={t("onboarding.new.otherPlaceholder")}
                      className="bg-white/10 border-white/20 text-white placeholder-white/50 text-lg px-6 py-4 h-auto min-h-[60px]"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          handleOtherSubmit()
                        }
                      }}
                    />
                    <Button
                      onClick={handleOtherSubmit}
                      disabled={!currentAnswer.trim()}
                      className="bg-vitamin-base hover:bg-vitamin-700 text-white"
                    >
                      {t("common.continue")} <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>
                ) : questions[currentQuestion].type === 'multi-select' ? (
                  <div className="space-y-3">
                    {questions[currentQuestion].options?.map((option) => (
                      <motion.button
                        key={option}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => toggleMarketingGoal(option)}
                        className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 flex items-center justify-between ${
                          selectedMarketingGoals.includes(option)
                            ? 'border-vitamin-base bg-vitamin-base/20 text-white'
                            : 'border-white/20 bg-white/5 text-white/70 hover:border-white/40'
                        }`}
                      >
                        <span className="text-lg">
                          {t(`onboarding.new.marketingGoals.${option}`)}
                        </span>
                        {selectedMarketingGoals.includes(option) && (
                          <Check className="h-5 w-5" />
                        )}
                      </motion.button>
                    ))}
                  </div>
                ) : questions[currentQuestion].type === 'select' ? (
                  <div className="space-y-3">
                    {questions[currentQuestion].options?.map((option) => (
                      <motion.button
                        key={option}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setCurrentAnswer(option)}
                        className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ${
                          currentAnswer === option
                            ? 'border-vitamin-base bg-vitamin-base/20 text-white'
                            : 'border-white/20 bg-white/5 text-white/70 hover:border-white/40'
                        }`}
                      >
                        <span className="text-lg">
                          {questions[currentQuestion].id === 'businessType' && t(`onboarding.new.businessTypes.${option}`)}
                          {questions[currentQuestion].id === 'businessSubtype' && t(`onboarding.new.businessSubtypes.${option}`)}
                          {questions[currentQuestion].id === 'targetAudience' && t(`onboarding.new.targetAudiences.${option}`)}
                          {questions[currentQuestion].id === 'toneOfVoice' && t(`onboarding.new.toneOfVoices.${option}`)}
                        </span>
                      </motion.button>
                    ))}
                  </div>
                ) : (
                  <Input
                    value={currentAnswer}
                    onChange={(e) => setCurrentAnswer(e.target.value)}
                    placeholder={questions[currentQuestion].id === 'businessName' ? t('onboarding.new.businessNamePlaceholder') : questions[currentQuestion].id === 'governorate' ? t('onboarding.new.governoratePlaceholder') : ''}
                    className="bg-white/10 border-white/20 text-white placeholder-white/50 text-lg px-6 py-4 h-auto min-h-[60px]"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleNext()
                      }
                    }}
                  />
                )}
                
                {!showOtherInput && (
                  <div className="flex justify-between mt-8">
                    <Button
                      variant="outline"
                      onClick={handlePrevious}
                      disabled={currentQuestion === 0}
                      className="border-white/20 text-black dark:text-white hover:bg-white/10"
                    >
                      <ArrowLeft className="mr-2 h-4 w-4" />
                      {t("common.previous")}
                    </Button>
                    
                    <Button
                      onClick={questions[currentQuestion].type === 'multi-select' ? handleMultiSelectNext : handleNext}
                      disabled={
                        (questions[currentQuestion].type === 'multi-select' && selectedMarketingGoals.length === 0) ||
                        (questions[currentQuestion].type !== 'multi-select' && !currentAnswer.trim()) ||
                        isSubmitting
                      }
                      className="bg-vitamin-base hover:bg-vitamin-700 text-white"
                    >
                      {isSubmitting ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          {t("common.loading", "Loading...")}
                        </>
                      ) : (
                        <>
                          {currentQuestion === questions.length - 1 ? t("common.complete") : t("common.next")}
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
