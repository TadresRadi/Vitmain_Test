import { useState, useEffect } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  LayoutDashboard,
  MessageSquare,
  HelpCircle,
  CreditCard,
  LogOut,
  Menu,
  X,
  Sparkles,
} from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useTranslation } from "react-i18next"
import AnimatedBackground from "@/components/AnimatedBackground"
import api from "@/lib/axios"
import type { UsageResponse } from "@/types/api"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuthStore()
  const { t } = useTranslation()
  const [planSlug, setPlanSlug] = useState<string | null>(null)

  useEffect(() => {
    api.get<UsageResponse>("/users/usage")
      .then((res) => setPlanSlug(res.data.plan_slug))
      .catch(() => setPlanSlug(null))
  }, [])

  const sidebarItems = [
    { icon: LayoutDashboard, label: t("dashboardLayout.dashboard"), path: "/dashboard" },
    ...(planSlug !== "pro"
      ? [{ icon: MessageSquare, label: t("dashboardLayout.campaigns"), path: "/chat" }]
      : []),
    { icon: CreditCard, label: t("dashboardLayout.subscription"), path: "/subscription" },
    { icon: HelpCircle, label: t("dashboardLayout.support", "Support"), path: "/support" },
  ]


  return (
    <div className="min-h-screen flex relative text-white bg-black/40 dark:bg-black/60 transition-colors duration-1000">
      <AnimatedBackground />
      
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 z-50 h-screen w-64 border-r border-white/20 bg-black/60 backdrop-blur-md flex flex-col transition-transform md:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between h-16 px-4 border-b border-white/20">
          <Link to="/" className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-vitamin-base" />
            <span className="font-bold text-white">Vitamin</span>
          </Link>
          <button className="md:hidden" onClick={() => setSidebarOpen(false)}>
            <X className="h-5 w-5 text-white" />
          </button>
        </div>

        <ScrollArea className="flex-1 py-4">
          <nav className="px-3 space-y-1">
            {sidebarItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  location.pathname === item.path
                    ? "bg-vitamin-base text-white"
                    : "text-white/70 hover:bg-white/10 hover:text-white"
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </nav>
        </ScrollArea>

        <div className="p-4 border-t border-white/20">
          <Button
            variant="ghost"
            className="w-full justify-start text-white hover:bg-white/10"
            onClick={() => {
              logout()
              navigate("/")
            }}
          >
            <LogOut className="mr-2 h-4 w-4" />
            {t("dashboardLayout.logout")}
          </Button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 relative z-10">
        <header className="sticky top-0 z-30 h-16 border-b border-white/20 bg-black/40 backdrop-blur-md flex items-center px-4 md:px-8">
          <button
            className="md:hidden mr-4 rounded-lg p-2 hover:bg-white/10"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5 text-white" />
          </button>
          <h1 className="text-lg font-semibold capitalize text-white">
            {sidebarItems.find((i) => i.path === location.pathname)?.label || "Dashboard"}
          </h1>
        </header>
        <main className="flex-1 p-4 md:p-8 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
