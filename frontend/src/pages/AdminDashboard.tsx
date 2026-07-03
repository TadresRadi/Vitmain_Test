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
import { adminApi } from "@/lib/axios"
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
      const res = await adminApi.get("/admin/overview")
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
      const res = await adminApi.get(`/admin/users/${user.id}/logs`)
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

      {/* USER TIMELINE ACTIVITY LOGS MODAL OVERLAY */}
      <AnimatePresence>
        {selectedUserForLogs && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md"
          >
            <motion.div 
              initial={{ scale: 0.96, y: 15 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.96, y: 15 }}
              className="w-full max-w-2xl bg-gradient-to-b from-neutral-900 to-black border border-red-500/30 rounded-2xl overflow-hidden flex flex-col max-h-[85vh] shadow-2xl"
            >
              {/* Modal Header */}
              <div className="p-5 border-b border-white/5 bg-white/5 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <ListOrdered className="w-5 h-5 text-red-500" />
                    Activity Logs Timeline: {selectedUserForLogs.full_name || 'Anonymous User'}
                  </h3>
                  <p className="text-xs text-white/40 mt-1">{selectedUserForLogs.email}</p>
                </div>
                <Button 
                  onClick={() => { setSelectedUserForLogs(null); setUserLogs(null); }}
                  variant="ghost" 
                  size="icon" 
                  className="text-white/60 hover:text-white hover:bg-white/10"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>

              {/* Modal Body */}
              <ScrollArea className="flex-1 p-6">
                {loadingLogs ? (
                  <div className="py-20 flex flex-col items-center justify-center gap-3 text-white/40 text-xs">
                    <Loader2 className="w-8 h-8 animate-spin text-red-500" />
                    <span>Accessing timeline audits...</span>
                  </div>
                ) : !userLogs || userLogs.length === 0 ? (
                  <div className="py-20 text-center text-white/40 text-xs flex flex-col items-center justify-center gap-3">
                    <Clock className="w-10 h-10 text-white/15" />
                    <span>No event logs found for this user account.</span>
                  </div>
                ) : (
                  <div className="space-y-6 relative border-l border-white/10 pl-6 ml-3">
                    {userLogs.map((log, index) => (
                      <div key={log.id || index} className="relative">
                        
                        {/* Timeline Bullet */}
                        <div className="absolute -left-[31px] top-1.5 w-3 h-3 rounded-full bg-red-500 border-2 border-black flex items-center justify-center ring-4 ring-red-500/10 shadow shadow-red-500/50" />
                        
                        <div className="space-y-1.5">
                          <div className="flex items-center gap-3">
                            <Badge className="bg-red-500/10 border border-red-500/30 text-red-400 font-mono text-[10px] py-0.5 px-2">
                              {log.action}
                            </Badge>
                            <span className="text-[10px] text-white/40 flex items-center gap-1 font-mono">
                              <Clock className="w-3 h-3" />
                              {new Date(log.created_at).toLocaleString()}
                            </span>
                          </div>
                          
                          {/* Log details */}
                          {log.details && (
                            <div className="bg-white/5 border border-white/5 rounded-lg p-3 text-[11px] text-white/70 overflow-x-auto leading-relaxed max-w-full">
                              {log.details.onboarding_answers && (
                                <div className="mb-3">
                                  <p className="text-red-400 font-semibold mb-2">Onboarding Questions & Answers:</p>
                                  {Object.entries(log.details.onboarding_answers).map(([question, answer], idx) => (
                                    <div key={idx} className="mb-1.5">
                                      <span className="text-white/50">{question}:</span>
                                      <span className="text-white/80 ml-2">{String(answer)}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                              {log.details.payment_status && (
                                <div className="mb-3">
                                  <p className="text-red-400 font-semibold mb-2">Payment Status:</p>
                                  <p className={log.details.payment_status === 'completed' ? 'text-green-400' : 'text-yellow-400'}>
                                    {log.details.payment_status === 'completed' ? 'Payment Completed' : log.details.payment_status}
                                  </p>
                                  {log.details.amount && (
                                    <p className="text-white/80 mt-1">Amount: {log.details.amount} EGP</p>
                                  )}
                                </div>
                              )}
                              {log.details.error && (
                                <div className="mb-3">
                                  <p className="text-red-400 font-semibold mb-2">Error Details:</p>
                                  <p className="text-red-300">{log.details.error}</p>
                                </div>
                              )}
                              {!log.details.onboarding_answers && !log.details.payment_status && !log.details.error && (
                                <pre className="font-mono">{JSON.stringify(log.details, null, 2)}</pre>
                              )}
                            </div>
                          )}
                        </div>

                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>

              {/* Modal Footer */}
              <div className="p-4 border-t border-white/5 bg-white/5 flex justify-end">
                <Button 
                  onClick={() => { setSelectedUserForLogs(null); setUserLogs(null); }}
                  className="bg-red-600 hover:bg-red-700 text-white px-5"
                >
                  Close Audits
                </Button>
              </div>

            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  )
}
