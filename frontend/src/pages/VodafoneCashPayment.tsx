import { useState, useEffect } from "react"
import { useNavigate, useSearchParams, useLocation } from "react-router-dom"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Copy, Check, Loader2 } from "lucide-react"
import AnimatedBackground from "@/components/AnimatedBackground"
import { useToast } from "@/hooks/use-toast"
import { useTranslation } from "react-i18next"
import api from "@/lib/axios"
import { getRegenerationOption, clearRegenerationOption } from "@/services/regenerationFlowService"

export default function VodafoneCashPayment() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const location = useLocation()
  const { toast } = useToast()
  const { t } = useTranslation()

  const planName = searchParams.get("plan_name") || "Professional Plan"
  const planSlug = searchParams.get("plan") || "basic"

  // Check if this is a regeneration flow
  const isRegenerationFlow = (location.state as { isRegenerationFlow?: boolean })?.isRegenerationFlow || false
  const regenerationOption = (location.state as { regenerationOption?: string })?.regenerationOption || getRegenerationOption()

  const [amount, setAmount] = useState(
    parseFloat(searchParams.get("amount") || "200")
  )
  const [phoneNumber, setPhoneNumber] = useState("")
  const [copied, setCopied] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [paymentStatus, setPaymentStatus] = useState<"idle" | "waiting" | "completed" | "failed">("idle")
  const [partialPayment, setPartialPayment] = useState<{
    received: number
    remaining: number
  } | null>(null)
  const [orderId, setOrderId] = useState<string | null>(null)
  const [receiverNumber, setReceiverNumber] = useState("01094064044")
  const [checkingPayment, setCheckingPayment] = useState(true)

  // تحقق من وجود طلب دفع سابق مرة واحدة فقط عند تحميل الصفحة
useEffect(() => {
  const savedOrderId = localStorage.getItem("payment_order_id")
  const savedPlan = localStorage.getItem("payment_plan")

  if (!savedOrderId || savedPlan !== planSlug) {
    if (savedOrderId && savedPlan !== planSlug) {
      localStorage.removeItem("payment_order_id")
      localStorage.removeItem("payment_plan")
    }

    setCheckingPayment(false)
    return
  }

  const restoreOrder = async () => {
    try {
      const response = await api.get(
        `/payments/order-status/${savedOrderId}/`
      )

      setOrderId(savedOrderId)
      setAmount(Number(response.data.remaining_amount))

      if (response.data.status === "completed") {
        localStorage.removeItem("payment_order_id")
        localStorage.removeItem("payment_plan")

        navigate(response.data.next_url || "/chat", {
          replace: true,
        })
        return
      }

      if (
        response.data.status === "pending" ||
        response.data.status === "partial"
      ) {
        setPaymentStatus("waiting")

        if (response.data.status === "partial") {
          setPartialPayment({
            received: Number(response.data.received_amount),
            remaining: Number(response.data.remaining_amount),
          })
        }
      } else {
        localStorage.removeItem("payment_order_id")
        localStorage.removeItem("payment_plan")
      }
    } catch {
      localStorage.removeItem("payment_order_id")
      localStorage.removeItem("payment_plan")
    } finally {
      setCheckingPayment(false)
    }
  }

  void restoreOrder()
}, [navigate, planSlug])


  const validatePhoneNumber = (phone: string): boolean => {
    const cleanPhone = phone.replace(/\s+/g, "")
    return /^(010|011|012|015)\d{8}$/.test(cleanPhone)
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(receiverNumber)
    setCopied(true)
    toast({
      title: t("vodafoneCashPayment.copiedToClipboard"),
      description: receiverNumber,
    })
    setTimeout(() => setCopied(false), 2000)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validatePhoneNumber(phoneNumber)) {
      toast({
        title: "Invalid Phone Number",
        description: "Please enter a valid Egyptian mobile number (010, 011, 012, or 015 followed by 8 digits).",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)

    try {
      const response = await api.post("/payments/create-order/", {
        expected_sender_number: phoneNumber,
        plan: planSlug,
      })

      setOrderId(response.data.id)
      setAmount(response.data.amount)
      setReceiverNumber(response.data.receiver_number)
      setPaymentStatus("waiting")

      localStorage.setItem("payment_order_id", response.data.id)
      localStorage.setItem("payment_plan", planSlug)

      toast({
        title: "Payment Order Created",
        description: `Reference code: ${response.data.reference_code}`,
      })
    } catch (error: any) {
      console.error("Failed to create payment order:", error)
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to create payment order. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  useEffect(() => {
    if (paymentStatus !== "waiting" || !orderId) return

    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/payments/order-status/${orderId}/`)

if (response.data.status === "completed") {
  clearInterval(pollInterval)
  setPaymentStatus("completed")

  localStorage.removeItem("payment_order_id")
  localStorage.removeItem("payment_plan")

  toast({
    title: "Payment Verified!",
    description:
      "Your subscription has been activated successfully.",
  })

  window.setTimeout(() => {
    // Handle regeneration flow after payment
    if (isRegenerationFlow && regenerationOption) {
      clearRegenerationOption()
      
      if (regenerationOption === "new_business_info") {
        // After new business info flow, go to chat with auto-start
        navigate("/chat", { 
          state: { autoStartCampaign: true },
          replace: true 
        })
      } else if (regenerationOption === "existing_business_info") {
        // After existing business info flow, go to chat with auto-start
        navigate("/chat", { 
          state: { autoStartCampaign: true },
          replace: true 
        })
      } else {
        navigate(response.data.next_url || "/chat", {
          replace: true,
        })
      }
    } else {
      navigate(response.data.next_url || "/chat", {
        replace: true,
      })
    }
  }, 1500)
} else if (response.data.status === "partial") {

          setPaymentStatus("waiting")
          setPartialPayment({
            received: Number(response.data.received_amount),
            remaining:
              Number(response.data.expected_amount) - Number(response.data.received_amount),
          })
        } else if (response.data.status === "failed") {
          setPaymentStatus("failed")
          clearInterval(pollInterval)

          toast({
            title: "Payment Failed",
            description: "The payment could not be verified. Please try again.",
            variant: "destructive",
          })
        }
      } catch (error) {
        console.error("Failed to check payment status:", error)
      }
    }, 3000)

    return () => clearInterval(pollInterval)
  }, [paymentStatus, orderId, navigate, toast])

  if (checkingPayment) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="animate-spin" />
      </div>
    )
  }

  if (paymentStatus === "idle") {
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
            <Card className="glass-dark border border-white/20 p-8">
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="text-center mb-8">
                  <h1 className="text-4xl font-bold text-white mb-4">
                    {t("vodafoneCashPayment.title")}
                  </h1>
                  <p className="text-white/70 text-lg">
                    {t("vodafoneCashPayment.completeSubscription", { planName })}
                  </p>
                </div>

                <div className="bg-vitamin-base/10 border border-vitamin-base/30 rounded-lg p-6 mb-8">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-white/70 text-lg">{t("vodafoneCashPayment.amountToPay")}</span>
                    <span className="text-4xl font-bold text-vitamin-base">{amount} EGP</span>
                  </div>

                  <div className="border-t border-white/10 pt-4 mt-4">
                    <p className="text-white/60 text-sm mb-2">{t("vodafoneCashPayment.transferToNumber")}</p>
                    <div className="flex items-center gap-3">
                      <span className="text-2xl font-bold text-white">{receiverNumber}</span>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handleCopy}
                        className="min-w-[100px] font-medium border-gray-300 text-gray-900 hover:bg-gray-100 dark:border-white/30 dark:text-white dark:hover:bg-white/20"
                      >
                        {copied ? (
                          <>
                            <Check className="h-4 w-4 mr-1" />
                            <span className="text-xs">{t("vodafoneCashPayment.copied")}</span>
                          </>
                        ) : (
                          <>
                            <Copy className="h-4 w-4 mr-1" />
                            <span className="text-xs">{t("vodafoneCashPayment.copy")}</span>
                          </>
                        )}
                      </Button>
                    </div>
                  </div>

                  <p className="text-white/60 text-sm mt-4">
                    {t("vodafoneCashPayment.transferInstructions", { amount })}
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-white mb-2 text-lg font-medium">
                      {t("vodafoneCashPayment.mobileNumberLabel")}
                    </label>
                    <Input
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder={t("vodafoneCashPayment.mobileNumberPlaceholder")}
                      className="bg-white/10 border-white/20 text-white placeholder-white/50 text-lg px-6 py-4 h-auto min-h-[60px]"
                      disabled={isSubmitting}
                    />
                    <p className="text-white/50 text-sm mt-2">
                      {t("vodafoneCashPayment.mobileNumberHint")}
                    </p>
                  </div>

                  <Button
                    type="submit"
                    disabled={isSubmitting || !phoneNumber.trim()}
                    className="w-full bg-vitamin-base hover:bg-vitamin-700 text-white py-4 text-lg font-medium"
                  >
                    {isSubmitting ? (
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    ) : (
                      t("vodafoneCashPayment.transferredButton")
                    )}
                  </Button>
                </form>

                <div className="mt-8 text-center">
                  <button
                    type="button"
                    onClick={() => navigate("/pricing")}
                    className="text-white/60 hover:text-white transition-colors"
                  >
                    {t("vodafoneCashPayment.cancelButton")}
                  </button>
                </div>
              </motion.div>
            </Card>
          </motion.div>
        </div>
      </div>
    )
  }

  if (paymentStatus === "waiting") {
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
            <Card className="glass-dark border border-white/20 p-8 text-center">
              <Loader2 className="h-16 w-16 text-vitamin-base animate-spin mx-auto mb-6" />
              <h2 className="text-3xl font-bold text-white mb-4">
                {t("vodafoneCashPayment.waitingTitle")}
              </h2>
              <p className="text-white/70 text-lg mb-6">
                {t("vodafoneCashPayment.waitingInstructions", { amount, receiverNumber })}
              </p>

              {partialPayment && (
                <div className="mt-6 p-4 rounded-lg bg-yellow-500/20 border border-yellow-400">
                  <h3 className="text-xl text-yellow-300 font-bold mb-3">
                    Partial Payment Received
                  </h3>
                  <p className="text-white">Paid: {partialPayment.received} EGP</p>
                  <p className="text-white">Remaining: {partialPayment.remaining} EGP</p>
                  <p className="text-white/70 mt-2">Waiting for remaining payment...</p>
                </div>
              )}

              <p className="text-white/50 text-sm">
                {t("vodafoneCashPayment.autoRedirect")}
              </p>
            </Card>
          </motion.div>
        </div>
      </div>
    )
  }

  if (paymentStatus === "completed") {
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
            <Card className="glass-dark border border-white/20 p-8 text-center">
              <Check className="h-16 w-16 text-green-500 mx-auto mb-6" />
              <h2 className="text-3xl font-bold text-white mb-4">
                {t("vodafoneCashPayment.verifiedTitle")}
              </h2>
              <p className="text-white/70 text-lg mb-6">
                {t("vodafoneCashPayment.verifiedInstructions")}
              </p>
              <Loader2 className="h-8 w-8 text-vitamin-base animate-spin mx-auto" />
            </Card>
          </motion.div>
        </div>
      </div>
    )
  }

  if (paymentStatus === "failed") {
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
            <Card className="glass-dark border border-white/20 p-8 text-center">
              <Loader2 className="h-16 w-16 text-red-500 mx-auto mb-6" />
              <h2 className="text-3xl font-bold text-white mb-4">
                {t("vodafoneCashPayment.failedTitle")}
              </h2>
              <p className="text-white/70 text-lg mb-6">
                {t("vodafoneCashPayment.failedInstructions")}
              </p>
              <Button
                onClick={() => {
                  setPaymentStatus("idle")
                  setOrderId(null)
                }}
                className="bg-vitamin-base hover:bg-vitamin-700 text-white"
              >
                {t("vodafoneCashPayment.tryAgain")}
              </Button>
              <div className="mt-4">
                <button
                  onClick={() => navigate("/pricing")}
                  className="text-white/60 hover:text-white transition-colors"
                >
                  {t("vodafoneCashPayment.returnToPricing")}
                </button>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    )
  }

  return null
}