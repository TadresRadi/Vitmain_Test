import { useState } from "react"
import { useNavigate, useSearchParams, useLocation } from "react-router-dom"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Check, ArrowRight, MessageSquare, Loader2 } from "lucide-react"
import { useTranslation } from "react-i18next"
import { useAuthStore } from "@/store/authStore"
import api from "@/lib/axios"
import { useToast } from "@/hooks/use-toast"
import { getRegenerationOption, clearRegenerationOption } from "@/services/regenerationFlowService"

interface Plan {
  id: number
  name: string
  slug: string
  price: number
  description: string
  features: string[]
  type: 'direct' | 'contact'
}

export default function Pricing() {
  const { t, i18n } = useTranslation()
  const isArabic = i18n.language === 'ar'
  
  const plans: Plan[] = [
    {
      id: 1,
      name: t("pricingPlans.professional"),
      slug: "basic",
      price: 200,
      description: t("pricingPlans.basicDesc"),
      features: (t("pricingPlans.basicFeatures", { returnObjects: true }) as string[]),
      type: 'direct'
    },
    {
      id: 2,
      name: t("pricingPlans.fullMarketingPlan"),
      slug: "pro",
      price: 5000,
      description: t("pricingPlans.premiumDesc"),
      features: (t("pricingPlans.premiumFeatures", { returnObjects: true }) as string[]),
      type: 'direct'
    }
  ]

  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const selectedPlan = searchParams.get("plan")
  const { isAuthenticated } = useAuthStore()
  const { toast } = useToast()
  const [submittingPlanId, setSubmittingPlanId] = useState<number | null>(null)
  const location = useLocation()
  
  // Check if this is a regeneration flow from onboarding
  const isRegenerationFlow = (location.state as { isRegenerationFlow?: boolean })?.isRegenerationFlow || false

  const handlePlanAction = async (plan: Plan) => {
    if (isAuthenticated) {
      setSubmittingPlanId(plan.id)
      try {
        const response = await api.post("/subscription/subscribe", { plan_slug: plan.slug })
        
        toast({
          title: t("common.success", "Success"),
          description: response.data.message,
        })
        
        // Check if the response indicates redirect to payment page
        if (response.data.action === "redirect_payment") {
          // Redirect to Vodafone Cash payment page with regeneration flow info
          const regenerationOption = getRegenerationOption()
          navigate(`/payment/vodafone-cash?plan=${response.data.plan_slug}&plan_name=${response.data.plan_name}&amount=${response.data.amount}`, {
            state: { 
              isRegenerationFlow: isRegenerationFlow || regenerationOption !== null,
              regenerationOption: regenerationOption
            }
          })
          return
        }
        
        // Check if user is coming from regeneration flow (for direct subscription without payment)
        const regenerationOption = getRegenerationOption()
        
        if (regenerationOption === "new_business_info") {
          // Clear the option and redirect to onboarding
          clearRegenerationOption()
          navigate('/new-onboarding')
          return
        } else if (regenerationOption === "existing_business_info") {
          // Clear the option and trigger regeneration with existing data
          clearRegenerationOption()
          try {
            await api.post("/chat/premium-posts")
            toast({
              title: t("chat.generationSuccess", "Campaign Formulated"),
              description: t("chat.generationSuccessDesc", "10 marketing posts have been tailored to your business profile!"),
            })
          } catch (err: any) {
            console.error("Failed to regenerate posts:", err)
            toast({
              title: t("common.error", "Error"),
              description: t("chat.failedToGenerate", "Failed to generate posts. Please try again."),
              variant: "destructive",
            })
          }
          navigate('/chat')
          return
        }
        
        const redirectAction = response.data.action as string | undefined

        if (redirectAction === "redirect_chat") {
          // Required flow:
          // - If user selected the 200 EGP plan (basic), start generating posts after plan selection.
          // - For other plans, follow existing redirect logic without forcing onboarding auto-generation.
          const shouldAutoStart = plan.slug === "basic"

          try {
            const onboardingRes = await api.get("/onboarding/")
            if (onboardingRes.data) {
              navigate("/chat", { state: { autoStartCampaign: shouldAutoStart }, replace: true })
            } else {
              navigate("/new-onboarding", { state: { autoStartCampaign: shouldAutoStart }, replace: true })
            }
          } catch {
            navigate("/new-onboarding", { state: { autoStartCampaign: shouldAutoStart }, replace: true })
          }
          return
        }

        if (redirectAction === "redirect_support") {
          navigate("/support", { replace: true })
          return
        }
      } catch (err: any) {
        console.error(err)
        toast({
          title: t("common.error", "Error"),
          description: err.response?.data?.detail || err.response?.data?.error || t("subscription.failed", "Failed to activate subscription. Please try again."),
          variant: "destructive",
        })
      } finally {
        setSubmittingPlanId(null)
      }
    } else {
      navigate(`/register?plan=${plan.slug}`)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="relative z-10 min-h-screen pt-24 pb-20">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="text-5xl font-bold text-white mb-6">{t("pricing.title")}</h1>
            <p className="text-xl text-white/80 max-w-2xl mx-auto">
              {t("pricing.description")}
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-12 max-w-4xl mx-auto">
            {plans.map((plan, i) => (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.2 }}
                id={`plan-${plan.slug}`}
              >
                <Card
                  className={`h-full relative transition-all duration-300 cursor-pointer ${
                    plan.slug === "pro" 
                      ? "glass-dark border-vitamin-base/50 hover:scale-105" 
                      : "glass-dark border-white/20 hover:scale-105"
                  } ${selectedPlan === plan.slug ? "ring-2 ring-vitamin-base shadow-2xl shadow-vitamin-base/20" : ""} ${submittingPlanId !== null ? "pointer-events-none opacity-50" : ""}`}
                  onClick={() => submittingPlanId === null && handlePlanAction(plan)}
                >
                  {plan.slug === "pro" && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <div className="bg-vitamin-base text-white px-6 py-2 rounded-full text-sm font-medium">
                        {t("pricingPlans.mostPopular")}
                      </div>
                    </div>
                  )}
                  
                  <div className="p-8">
                    <div className="text-center mb-8">
                      <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                      {plan.slug === "basic" && (
                        <p className="text-sm text-vitamin-base font-semibold mb-4">TESLA L MODLE</p>
                      )}
                      <div className="mb-4">
                        <span className="text-5xl font-bold text-vitamin-base">{plan.price}</span>
                        <span className="text-xl text-white/60 mx-2">{t("pricingPlans.currency")}</span>
                      </div>
                      <p className="text-white/70">{plan.description}</p>
                    </div>
                    
                    <div className="space-y-4 mb-8">
                      {plan.features.map((feature, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <Check className="h-5 w-5 text-vitamin-base shrink-0" />
                          <span className="text-white/80">{feature}</span>
                        </div>
                      ))}
                    </div>
                    
                    <Button
                      className={`w-full py-4 text-lg font-medium transition-all duration-300 ${
                        plan.type === 'direct'
                          ? "bg-vitamin-base hover:bg-vitamin-700 text-white"
                          : "border border-vitamin-base text-vitamin-base hover:bg-vitamin-base hover:text-white"
                      }`}
                      variant={plan.type === 'direct' ? 'default' : 'outline'}
                      disabled={submittingPlanId !== null}
                    >
                      {submittingPlanId === plan.id ? (
                        <Loader2 className="h-5 w-5 animate-spin mr-2" />
                      ) : plan.type === 'direct' ? (
                        <>
                          {t("pricingPlans.getStarted")} <ArrowRight className={`h-5 w-5 ${isArabic ? 'mr-2 rotate-180' : 'ml-2'}`} />
                        </>
                      ) : (
                        <>
                          <MessageSquare className={`h-5 w-5 ${isArabic ? 'ml-2' : 'mr-2'}`} /> {t("pricingPlans.contactSupport")}
                        </>
                      )}
                    </Button>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
