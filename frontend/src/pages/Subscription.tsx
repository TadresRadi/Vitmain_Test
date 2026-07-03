import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import DashboardLayout from "@/components/DashboardLayout"
import api from "@/lib/axios"
import { Check, X, Zap, ArrowRight } from "lucide-react"
import { useTranslation } from "react-i18next"

interface UsageStats {
  total_images: number
  max_images: number
  remaining_images: number
  plan_name: string | null
  has_access: boolean
  total_amount_paid: number
}

export default function Subscription() {
  const [usage, setUsage] = useState<UsageStats | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { t } = useTranslation()

  useEffect(() => {
    api.get("/users/usage").then((res) => {
      setUsage(res.data)
      setLoading(false)
    })
  }, [])

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h2 className="text-2xl font-bold">{t("subscription.title")}</h2>
          <p className="text-muted-foreground">{t("subscription.subtitle")}</p>
        </div>

        {loading ? (
          <Skeleton className="h-64 rounded-xl" />
        ) : usage?.has_access ? (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="h-5 w-5 text-primary" />
                      {usage.plan_name} {t("subscription.title")}
                    </CardTitle>
                    <CardDescription>{t("subscription.subtitle")}</CardDescription>
                  </div>
                  <Badge variant="default" className="bg-emerald-500 hover:bg-emerald-600">
                    {t("subscription.active")}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid sm:grid-cols-3 gap-4">
                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">{t("subscription.imagesGenerated")}</p>
                    <p className="text-2xl font-bold mt-1">{usage.total_images}</p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">{t("subscription.remaining")}</p>
                    <p className="text-2xl font-bold mt-1">0</p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">{t("subscription.totalAmountPaid")}</p>
                    <p className="text-2xl font-bold mt-1">{usage.total_amount_paid} EGP</p>
                  </div>
                </div>

                <div className="rounded-lg border p-4 space-y-2">
                  <p className="text-sm font-medium">{t("subscription.planFeatures")}</p>
                  <ul className="space-y-2">
                    <li className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-emerald-500" />
                      {t("subscription.featureImages", { count: usage.max_images })}
                    </li>
                    <li className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-emerald-500" />
                      {t("subscription.featureChat")}
                    </li>
                    <li className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-emerald-500" />
                      {t("subscription.featureDashboard")}
                    </li>
                  </ul>
                </div>

                <Button className="w-full" variant="outline" onClick={() => navigate("/pricing")}>
                  {t("subscription.changePlan")} <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="text-center py-12">
              <CardContent className="space-y-4">
                <div className="mx-auto h-16 w-16 rounded-full bg-muted flex items-center justify-center">
                  <X className="h-8 w-8 text-muted-foreground" />
                </div>
                <CardTitle>{t("subscription.noActivePlan")}</CardTitle>
                <CardDescription className="max-w-sm mx-auto">
                  {t("subscription.noPlanDesc")}
                </CardDescription>
                <Button onClick={() => navigate("/pricing")}>
                  {t("subscription.viewPlans")} <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  )
}
