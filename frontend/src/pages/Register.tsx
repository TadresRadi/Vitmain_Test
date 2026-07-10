import { useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import { useTranslation } from "react-i18next"
import { useAuthStore } from "@/store/authStore"
import { useToast } from "@/hooks/use-toast"
import api from "@/lib/axios"
import type { UsageResponse } from "@/types/api"
import vitaminLogo from "@/components/imge/vitamin-Logo-White.png"
import GoogleAuthButton from "@/components/GoogleAuthButton"

export default function Register() {
  const { t } = useTranslation()
  
  // Registration state
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [passwordConfirm, setPasswordConfirm] = useState("")
  const [fullName, setFullName] = useState("")
  const [phoneNumber, setPhoneNumber] = useState("")
  const [dob, setDob] = useState("")
  const [userType, setUserType] = useState("explorer")
  const [loading, setLoading] = useState(false)
  const [searchParams] = useSearchParams()
  const plan = searchParams.get("plan")
  
  const register = useAuthStore((state) => state.register)
  const navigate = useNavigate()
  const { toast } = useToast()

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (password !== passwordConfirm) {
      toast({
        title: t("common.error", "Error"),
        description: t("register.passwordMismatch", "Passwords do not match."),
        variant: "destructive",
      })
      return
    }

    setLoading(true)
    try {
      await register(email, password, passwordConfirm, fullName, phoneNumber, dob, userType)
      
if (plan === "basic" || plan === "pro") {
  const subRes = await api.post("/subscription/subscribe", {
    plan_slug: plan,
  })

  toast({
    title: t("common.success", "Success"),
    description: t(
      "register.successMsg",
      "Registration successful! Welcome to Vitamin AI."
    ),
  })

  if (subRes.data.action === "redirect_payment") {
    const query = new URLSearchParams({
      plan: subRes.data.plan_slug,
      plan_name: subRes.data.plan_name,
      amount: String(subRes.data.amount),
    })

    navigate(`/payment/vodafone-cash?${query.toString()}`, {
      replace: true,
    })
    return
  }

  if (subRes.data.action === "redirect_support") {
    navigate("/support", { replace: true })
    return
  }
}

      toast({
        title: t("common.success", "Success"),
        description: t("register.successMsg", "Registration successful! Welcome to Vitamin AI."),
      })
      navigate("/new-onboarding")
    } catch (err: any) {
      console.error(err)
      toast({
        title: t("common.error", "Error"),
        description: err.response?.data?.detail || err.response?.data?.error || t("register.failedMsg", "Registration failed. Please try again."),
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

const handleGoogleSuccess = async () => {
  const { user } = useAuthStore.getState()

  if (!user?.onboarding_completed) {
    navigate("/new-onboarding", { replace: true })
    return
  }

  try {
    const usageRes = await api.get<UsageResponse>("/users/usage")

    if (usageRes.data.plan_slug === "pro") {
      navigate("/support", { replace: true })
    } else if (usageRes.data.has_access) {
      navigate("/chat", { replace: true })
    } else {
      navigate("/pricing", { replace: true })
    }
  } catch {
    navigate("/pricing", { replace: true })
  }
}


  return (
    <div className="relative z-10 pt-32 pb-20 px-4 min-h-screen flex items-center justify-center">
      <div className="relative z-10 w-full max-w-lg">
        <div className="flex justify-center mb-8">
          <Link to="/" className="flex items-center gap-2">
            <img
              src={vitaminLogo}
              alt="Vitamin Logo"
              className="w-8 h-8"
            />
            <span className="text-xl font-bold text-white">Vitamin</span>
          </Link>
        </div>
        
        <Card className="glass-dark border border-white/20 p-8 shadow-2xl backdrop-blur-md">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">{t("register.title")}</h2>
            <p className="text-white/70 text-sm">{t("register.description")}</p>
          </div>
          
          <div className="space-y-6">
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-white/70 mb-1">{t("register.fullNameLabel")}</label>
                <Input
                  placeholder={t("register.fullNamePlaceholder")}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  className="bg-white/5 border-white/10 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-white/70 mb-1">{t("register.emailLabel")}</label>
                  <Input
                    type="email"
                    placeholder={t("register.emailPlaceholder")}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="bg-white/5 border-white/10 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/70 mb-1">{t("register.phoneLabel")}</label>
                  <Input
                    type="tel"
                    placeholder={t("register.phonePlaceholder")}
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    required
                    className="bg-white/5 border-white/10 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-white/70 mb-1">{t("register.dobLabel")}</label>
                  <Input
                    type="date"
                    value={dob}
                    onChange={(e) => setDob(e.target.value)}
                    required
                    className="bg-white/5 border-white/10 text-white focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/70 mb-1">{t("register.userTypeLabel")}</label>
                  <select
                    value={userType}
                    onChange={(e) => setUserType(e.target.value)}
                    required
                    className="w-full h-10 px-3 rounded-md bg-slate-900 border border-white/10 text-white text-sm focus:border-vitamin-base focus:outline-none focus:ring-1 focus:ring-vitamin-base"
                  >
                    <option value="explorer">{t("register.explorer")}</option>
                    <option value="business_owner">{t("register.businessOwner")}</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-white/70 mb-1">{t("register.passwordLabel")}</label>
                  <Input
                    type="password"
                    placeholder={t("register.passwordPlaceholder")}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="bg-white/5 border-white/10 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/70 mb-1">{t("register.confirmPasswordLabel")}</label>
                  <Input
                    type="password"
                    placeholder={t("register.confirmPasswordPlaceholder")}
                    value={passwordConfirm}
                    onChange={(e) => setPasswordConfirm(e.target.value)}
                    required
                    className="bg-white/5 border-white/10 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base"
                  />
                </div>
              </div>
              
              <Button 
                type="submit" 
                className="w-full mt-2 bg-gradient-to-r from-vitamin-base to-purple-600 hover:from-vitamin-700 hover:to-purple-700 text-white font-medium shadow-lg transition-all duration-300 transform hover:scale-[1.01]" 
                disabled={loading}
              >
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                {t("register.createAccount")}
              </Button>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-white/20" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-slate-900 px-2 text-white/60">
                  {t("register.orContinueWith")}
                </span>
              </div>
            </div>

            <GoogleAuthButton mode="register" onSuccess={handleGoogleSuccess} />
          </div>
          
          <p className="mt-6 text-center text-sm text-white/60">
            {t("register.haveAccount")}{" "}
            <Link to="/login" className="text-vitamin-base font-semibold hover:underline">
              {t("register.signIn")}
            </Link>
          </p>
        </Card>
      </div>
    </div>
  )
}
