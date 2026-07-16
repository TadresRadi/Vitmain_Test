import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Users,
  BarChart3,
  Shield,
  LogOut,
  ListOrdered,
  Clock,
  Loader2,
  X,
  FileText,
  Languages,
  FolderOpen,
  Star,
  Image as ImageIcon,
  MessageSquare,
  Car
} from "lucide-react"
import { useAdminAuthStore } from "@/store/adminAuthStore"
import { api } from "@/lib/axios"
import { motion, AnimatePresence } from "framer-motion"
import OverviewSection from "@/components/admin/OverviewSection"
import UsersSection from "@/components/admin/UsersSection"
import ProjectsSection from "@/components/admin/ProjectsSection"
import FeaturedProjectsSection from "@/components/admin/FeaturedProjectsSection"
import BrandsSection from "@/components/admin/BrandsSection"
import TeslaClientSection from "@/components/admin/TeslaClientSection"
import SuccessStoriesSection from "@/components/admin/SuccessStoriesSection"
import SupportSection from "@/components/admin/SupportSection"

export default function AdminDashboard() {
  const { t, i18n } = useTranslation()
  const { adminLogout, adminUser } = useAdminAuthStore()
  const [activeTab, setActiveTab] = useState('overview')
  const [overviewData, setOverviewData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  // Timeline Logs modal state
  const [selectedUserForLogs, setSelectedUserForLogs] = useState<any | null>(null)
  const [userLogs, setUserLogs] = useState<any[] | null>(null)
  const [loadingLogs, setLoadingLogs] = useState(false)

  // Force supervisor to support tab
  useEffect(() => {
    if (adminUser?.role === 'supervisor') {
      setActiveTab('support')
    }
  }, [adminUser])

  const fetchOverview = async () => {
    try {
      const res = await api.get("/admin/overview")
      setOverviewData(res.data)
    } catch (err: any) {
      console.error('Failed to fetch overview:', err)
    }
  }

  useEffect(() => {
    if (adminUser?.role === 'super_admin') {
      fetchOverview()
    }
    setLoading(false)
  }, [adminUser])

  // Fetch timeline audit logs for user
  const handleOpenUserLogs = async (user: any) => {
    setSelectedUserForLogs(user)
    setLoadingLogs(true)
    try {
      const res = await api.get(`/admin/users/${user.id}/logs`)
      setUserLogs(res.data)
    } catch (err) {
      console.error("Failed to load user activity logs", err)
      alert(t('adminDashboard.failedLoadLogs'))
      setSelectedUserForLogs(null)
    } finally {
      setLoadingLogs(false)
    }
  }

  const handleLogout = () => {
    adminLogout()
    window.location.href = '/admin-login'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="animate-spin h-8 w-8 border-4 border-red-600 border-t-transparent rounded-full" />
        <span className="ml-3 text-white">{t('adminDashboard.loading', "Accessing Secure Core...")}</span>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', label: t('adminDashboard.overview', "Overview"), icon: BarChart3, roles: ['super_admin'] },
    { id: 'users', label: t('adminDashboard.users', "Users"), icon: Users, roles: ['super_admin'] },
    { id: 'projects', label: t('adminDashboard.projects', "Projects"), icon: FolderOpen, roles: ['super_admin', 'supervisor'] },
    { id: 'featuredProjects', label: t('adminDashboard.featuredProjects', "Featured Projects"), icon: Star, roles: ['super_admin', 'supervisor'] },
    { id: 'brands', label: t('adminDashboard.brands', "Brands"), icon: ImageIcon, roles: ['super_admin', 'supervisor'] },
    { id: 'teslaClient', label: t('adminDashboard.teslaClient', "Tesla Client"), icon: Car, roles: ['super_admin', 'supervisor'] },
    { id: 'successStory', label: t('adminDashboard.successStory', "Success Story"), icon: FileText, roles: ['super_admin', 'supervisor'] },
    { id: 'support', label: t('adminDashboard.supportChat', "Support Hub"), icon: MessageSquare, roles: ['super_admin', 'supervisor'] },
  ].filter(tab => tab.roles.includes(adminUser?.role || ''))

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-950/20 via-black to-red-950/30 text-white font-sans pb-16">
      
      {/* Top Header */}
      <header className="border-b border-red-500/20 bg-black/45 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-red-500 animate-pulse" />
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                {t('adminDashboard.title', "Vitamin AI Command Console")}
                <Badge className="bg-red-500/20 border border-red-500/30 text-red-500 text-[10px] uppercase font-bold px-2 py-0.5">
                  {adminUser?.role}
                </Badge>
              </h1>
              <p className="text-xs text-white/50">{t('adminDashboard.subtitle', "SaaS platform control & auditing interface")}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={() => {
                const currentLang = i18n.language;
                i18n.changeLanguage(currentLang === 'en' ? 'ar' : 'en');
              }}
              variant="outline"
              className="border-red-500/30 text-red-400 hover:bg-red-500/10"
            >
              <Languages className="w-4 h-4 mr-2" />
              {t('common.language', 'Language')}
            </Button>
            <Button onClick={handleLogout} variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-500/10">
              <LogOut className="w-4 h-4 mr-2" />
              {t('adminDashboard.logout', "Terminate Session")}
            </Button>
          </div>
        </div>
      </header>

      {/* Tabs Controller */}
      <div className="border-b border-red-500/20 bg-black/20 backdrop-blur-sm sticky top-[73px] z-30">
        <div className="max-w-7xl mx-auto px-6">
          <nav className="flex gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-5 py-4 text-sm font-semibold transition-all border-b-2 ${
                  activeTab === tab.id
                    ? 'text-red-500 border-red-500 bg-red-500/5'
                    : 'text-white/60 border-transparent hover:text-white hover:bg-white/5'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Workspace Pages */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && adminUser?.role === 'super_admin' && (
          <OverviewSection data={overviewData} />
        )}

        {/* USERS TAB */}
        {activeTab === 'users' && adminUser?.role === 'super_admin' && (
          <UsersSection onOpenUserLogs={handleOpenUserLogs} />
        )}

        {/* PROJECTS TAB */}
        {activeTab === 'projects' && (
          <ProjectsSection />
        )}

        {/* FEATURED PROJECTS TAB */}
        {activeTab === 'featuredProjects' && (
          <FeaturedProjectsSection />
        )}

        {/* BRANDS TAB */}
        {activeTab === 'brands' && (
          <BrandsSection />
        )}

        {/* TESLA CLIENT TAB */}
        {activeTab === 'teslaClient' && (
          <TeslaClientSection />
        )}

        {/* SUCCESS STORY TAB */}
        {activeTab === 'successStory' && (
          <SuccessStoriesSection />
        )}

        {/* SUPPORT HUB TAB (AVAILABLE TO BOTH ADMIN AND SUPERVISOR) */}
        {activeTab === 'support' && (
          <SupportSection />
        )}

      </main>
    </div>
  )
}
