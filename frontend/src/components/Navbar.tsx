import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui/button"
import { Menu, X, Sun, Moon } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import LanguageSwitcher from "./LanguageSwitcher"
import { useTranslation } from "react-i18next"
import LogoImage from "./imge/vitamin-Logo-White.png"
import api from "@/lib/axios"
import type { UsageResponse } from "@/types/api"

export default function Navbar() {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const [isDark, setIsDark] = useState(true)
  const { isAuthenticated, logout } = useAuthStore()
  const navigate = useNavigate()
  const [planSlug, setPlanSlug] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      setPlanSlug(null)
      return
    }
    api.get<UsageResponse>("/users/usage")
      .then((res) => setPlanSlug(res.data.plan_slug))
      .catch(() => setPlanSlug(null))
  }, [isAuthenticated])

  const navLinks = [
    { name: t("navbar.home"), path: "/" },
    { name: t("navbar.about", { defaultValue: "About Us" }), path: "/about" },
    { name: t("navbar.work", { defaultValue: "Our Work" }), path: "/work" },
    { name: t("navbar.pricing"), path: "/pricing" },

    // NEW: Tesla
    { name: t("navbar.teslaClients", { defaultValue: "Tesla Clients" }), path: "/tesla-clients" },

    { name: t("contact.title"), path: "/contact" },

    ...(isAuthenticated && planSlug !== "pro"
      ? [{ name: t("navbar.chat"), path: "/chat" }]
      : []),
  ]

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle("dark")
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/5 backdrop-blur-[7px] dark:border-white/30 shadow-2xl bg-gradient-to-b from-white/10 via-white/5 to-transparent">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <img src={LogoImage} alt="Vitamin" className="h-8" />
            <span className="text-xl font-bold text-white">Vitamin</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className="text-sm font-medium text-white hover:text-white transition-colors"
              >
                {link.name}
              </Link>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            <LanguageSwitcher />
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="gap-1.5 font-semibold text-white/70 hover:text-white hover:bg-white/10"
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            {isAuthenticated ? (
              <>
                <Button
                  variant="outline"
                  onClick={() => navigate("/dashboard")}
                  className="border-border text-foreground hover:bg-accent dark:border-white/20 dark:text-white dark:hover:bg-white/10"
                >
                  {t("navbar.dashboard")}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => { logout(); navigate("/") }}
                  className="border-border text-foreground hover:bg-accent dark:border-white/20 dark:text-white dark:hover:bg-white/10"
                >
                  {t("navbar.logout")}
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="outline"
                  onClick={() => navigate("/login")}
                  className="border-border text-foreground hover:bg-accent dark:border-white/20 dark:text-white dark:hover:bg-white/10"
                >
                  {t("navbar.login")}
                </Button>
                <Button
                  onClick={() => navigate("/register")}
                  className="border-border text-foreground hover:bg-accent dark:border-white/20 dark:text-white dark:hover:bg-white/10"
                >
                  {t("navbar.getStarted")}
                </Button>
              </>
            )}
          </div>

          <button
            className="md:hidden rounded-lg p-2 hover:bg-accent text-foreground dark:hover:bg-white/10 dark:text-white"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-border glass-dark dark:border-white/10"
          >
            <div className="px-4 py-4 space-y-3">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  className="block py-2 text-sm font-medium text-white hover:text-white"
                  onClick={() => setIsOpen(false)}
                >
                  {link.name}
                </Link>
              ))}
              <div className="flex items-center gap-4 py-2">
                <LanguageSwitcher />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleTheme}
                  className="gap-1.5 font-semibold text-white/70 hover:text-white hover:bg-white/10"
                >
                  {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>
              </div>
              {isAuthenticated ? (
                <>
                  <Button 
                    className="w-full border-border text-foreground hover:bg-accent dark:border-white/20 dark:text-white dark:hover:bg-white/10" 
                    variant="outline" 
                    onClick={() => { setIsOpen(false); navigate("/dashboard") }}
                  >
                    {t("navbar.dashboard")}
                  </Button>
                  <Button 
                    className="w-full border-border text-foreground hover:bg-accent dark:border-white/20 dark:text-white dark:hover:bg-white/10" 
                    variant="outline" 
                    onClick={() => { setIsOpen(false); logout(); navigate("/") }}
                  >
                    {t("navbar.logout")}
                  </Button>
                </>
              ) : (
                <>
                  <Button 
                    className="w-full border-border text-foreground hover:bg-accent dark:border-white/20 dark:text-white dark:hover:bg-white/10" 
                    variant="outline" 
                    onClick={() => { setIsOpen(false); navigate("/login") }}
                  >
                    {t("navbar.login")}
                  </Button>
                  <Button 
                    className="w-full border-border text-foreground hover:bg-accent dark:border-white/20 dark:text-white dark:hover:bg-white/10" 
                    variant="outline" 
                    onClick={() => { setIsOpen(false); navigate("/register") }}
                  >
                    {t("navbar.getStarted")}
                  </Button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}
