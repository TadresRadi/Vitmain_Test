import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { useAuthStore } from "@/store/authStore"
import { useToast } from "@/hooks/use-toast"
import { Sparkles, Loader2 } from "lucide-react"
import { useTranslation } from "react-i18next"
import api from "@/lib/axios"
import type { UsageResponse } from "@/types/api"
import GoogleAuthButton from "@/components/GoogleAuthButton"

export default function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { t } = useTranslation()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await login(email, password)
      toast({ title: t("login.welcomeBack"), description: t("login.loginSuccess") })

      const usageRes = await api.get<UsageResponse>("/users/usage")

      if (usageRes.data.plan_slug === "pro") {
        navigate("/support", { replace: true })
      } else if (!response.user.onboarding_completed) {
        navigate("/new-onboarding")
      } else if (usageRes.data.has_access) {
        navigate("/chat", { replace: true })
      } else {
        navigate("/pricing", { replace: true })
      }
    } catch (err: any) {
      toast({
        title: t("login.loginFailed"),
        description: err.response?.data?.detail || t("login.invalidCredentials"),
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSuccess = async () => {
    const usageRes = await api.get<UsageResponse>("/users/usage")

    if (usageRes.data.plan_slug === "pro") {
      navigate("/support", { replace: true })
    } else if (usageRes.data.has_access) {
      navigate("/chat", { replace: true })
    } else {
      navigate("/pricing", { replace: true })
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
        <div className="flex justify-center mb-8">
          <Link to="/" className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Vitamin</span>
          </Link>
        </div>
        <Card>
          <CardHeader className="text-center">
            <CardTitle>{t("login.title")}</CardTitle>
            <CardDescription>
              {t("login.description")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t("login.email")}</label>
                  <Input
                    type="email"
                    placeholder={t("login.emailPlaceholder")}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t("login.password")}</label>
                  <Input
                    type="password"
                    placeholder={t("login.passwordPlaceholder")}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  {t("login.signIn")}
                </Button>
              </form>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    {t("login.orContinueWith")}
                  </span>
                </div>
              </div>

              <GoogleAuthButton mode="login" onSuccess={handleGoogleSuccess} />
            </div>
            <p className="mt-4 text-center text-sm text-muted-foreground">
              {t("login.noAccount")}{" "}
              <Link to="/register" className="text-primary hover:underline">
                {t("login.signUp")}
              </Link>
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
