import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Users,
  BarChart3,
  Shield,
  LogOut,
  Loader2,
  X,
  FileText,
  Languages,
  FolderOpen,
  Star,
  Image as ImageIcon,
  MessageSquare,
  Car,
} from 'lucide-react'
import { useAdminAuthStore } from '@/store/adminAuthStore'
import { api } from '@/lib/axios'
import { motion, AnimatePresence } from 'framer-motion'
import OverviewSection from '@/components/admin/OverviewSection'
import UsersSection from '@/components/admin/UsersSection'
import ProjectsSection from '@/components/admin/ProjectsSection'
import FeaturedProjectsSection from '@/components/admin/FeaturedProjectsSection'
import BrandsSection from '@/components/admin/BrandsSection'
import TeslaClientSection from '@/components/admin/TeslaClientSection'
import SuccessStoriesSection from '@/components/admin/SuccessStoriesSection'
import SupportSection from '@/components/admin/SupportSection'

export default function AdminDashboard() {
  const { t, i18n } = useTranslation()
  const { adminLogout, adminUser } = useAdminAuthStore()
  const [activeTab, setActiveTab] = useState('overview')
  const [overviewData, setOverviewData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  // User detail modal state
  const [selectedUserForLogs, setSelectedUserForLogs] = useState<any | null>(null)
  const [userDetail, setUserDetail] = useState<any | null>(null)
  const [loadingLogs, setLoadingLogs] = useState(false)

  // Force supervisor to support tab
  useEffect(() => {
    if (adminUser?.role === 'supervisor') {
      setActiveTab('support')
    }
  }, [adminUser])

  const fetchOverview = async () => {
    try {
      const res = await api.get('/admin/overview')
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

  // Fetch detailed user activity (payments, posts, images, onboarding)
  const handleOpenUserLogs = async (user: any) => {
    setSelectedUserForLogs(user)
    setLoadingLogs(true)
    setUserDetail(null)
    try {
      const res = await api.get(`/admin/users/${user.id}/details`)
      setUserDetail(res.data)
    } catch (err) {
      console.error('Failed to load user details', err)
      alert(t('adminDashboard.failedLoadLogs', 'Failed to load user details.'))
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
        <span className="ml-3 text-white">
          {t('adminDashboard.loading', 'Accessing Secure Core...')}
        </span>
      </div>
    )
  }

  const tabs = [
    {
      id: 'overview',
      label: t('adminDashboard.overview', 'Overview'),
      icon: BarChart3,
      roles: ['super_admin'],
    },
    { id: 'users', label: t('adminDashboard.users', 'Users'), icon: Users, roles: ['super_admin'] },
    {
      id: 'projects',
      label: t('adminDashboard.projects', 'Projects'),
      icon: FolderOpen,
      roles: ['super_admin', 'supervisor'],
    },
    {
      id: 'featuredProjects',
      label: t('adminDashboard.featuredProjects', 'Featured Projects'),
      icon: Star,
      roles: ['super_admin', 'supervisor'],
    },
    {
      id: 'brands',
      label: t('adminDashboard.brands', 'Brands'),
      icon: ImageIcon,
      roles: ['super_admin', 'supervisor'],
    },
    {
      id: 'teslaClient',
      label: t('adminDashboard.teslaClient', 'Tesla Client'),
      icon: Car,
      roles: ['super_admin', 'supervisor'],
    },
    {
      id: 'successStory',
      label: t('adminDashboard.successStory', 'Success Story'),
      icon: FileText,
      roles: ['super_admin', 'supervisor'],
    },
    {
      id: 'support',
      label: t('adminDashboard.supportChat', 'Support Hub'),
      icon: MessageSquare,
      roles: ['super_admin', 'supervisor'],
    },
  ].filter((tab) => tab.roles.includes(adminUser?.role || ''))

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-950/20 via-black to-red-950/30 text-white font-sans pb-16">
      {/* Top Header */}
      <header className="border-b border-red-500/20 bg-black/45 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-red-500 animate-pulse" />
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                {t('adminDashboard.title', 'Vitamin AI Command Console')}
                <Badge className="bg-red-500/20 border border-red-500/30 text-red-500 text-[10px] uppercase font-bold px-2 py-0.5">
                  {adminUser?.role}
                </Badge>
              </h1>
              <p className="text-xs text-white/50">
                {t('adminDashboard.subtitle', 'SaaS platform control & auditing interface')}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={() => {
                const currentLang = i18n.language
                i18n.changeLanguage(currentLang === 'en' ? 'ar' : 'en')
              }}
              variant="outline"
              className="border-red-500/30 text-red-400 hover:bg-red-500/10"
            >
              <Languages className="w-4 h-4 mr-2" />
              {t('common.language', 'Language')}
            </Button>
            <Button
              onClick={handleLogout}
              variant="outline"
              className="border-red-500/30 text-red-400 hover:bg-red-500/10"
            >
              <LogOut className="w-4 h-4 mr-2" />
              {t('adminDashboard.logout', 'Terminate Session')}
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
        {activeTab === 'projects' && <ProjectsSection />}

        {/* FEATURED PROJECTS TAB */}
        {activeTab === 'featuredProjects' && <FeaturedProjectsSection />}

        {/* BRANDS TAB */}
        {activeTab === 'brands' && <BrandsSection />}

        {/* TESLA CLIENT TAB */}
        {activeTab === 'teslaClient' && <TeslaClientSection />}

        {/* SUCCESS STORY TAB */}
        {activeTab === 'successStory' && <SuccessStoriesSection />}

        {/* SUPPORT HUB TAB (AVAILABLE TO BOTH ADMIN AND SUPERVISOR) */}
        {activeTab === 'support' && <SupportSection />}
      </main>

      {/* User Detail Modal */}
      <AnimatePresence>
        {selectedUserForLogs && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => {
              setSelectedUserForLogs(null)
              setUserDetail(null)
            }}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-dark border border-white/20 rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-red-500/20 border border-red-500/30 flex items-center justify-center">
                    <span className="text-red-400 font-bold text-lg">
                      {(selectedUserForLogs.full_name ||
                        selectedUserForLogs.email ||
                        '?')[0].toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      {selectedUserForLogs.full_name || 'Anonymous User'}
                    </h3>
                    <p className="text-sm text-white/50">{selectedUserForLogs.email}</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setSelectedUserForLogs(null)
                    setUserDetail(null)
                  }}
                  className="text-white/60 hover:text-white transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Loading State */}
              {loadingLogs && (
                <div className="flex items-center justify-center py-16">
                  <Loader2 className="h-8 w-8 text-red-500 animate-spin" />
                </div>
              )}

              {/* User Detail Content */}
              {!loadingLogs && userDetail && (
                <div className="space-y-6">
                  {/* Stats Grid */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-black/40 border border-white/10 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-red-400">
                        {userDetail.total_amount_paid || '0'}
                      </div>
                      <div className="text-xs text-white/50 mt-1 uppercase tracking-wider">
                        {t('adminDashboard.totalPaid', 'EGP Paid')}
                      </div>
                    </div>
                    <div className="bg-black/40 border border-white/10 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-red-400">
                        {userDetail.total_posts_generated || 0}
                      </div>
                      <div className="text-xs text-white/50 mt-1 uppercase tracking-wider">
                        {t('adminDashboard.totalPosts', 'Posts')}
                      </div>
                    </div>
                    <div className="bg-black/40 border border-white/10 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-red-400">
                        {userDetail.total_images_generated || 0}
                      </div>
                      <div className="text-xs text-white/50 mt-1 uppercase tracking-wider">
                        {t('adminDashboard.totalImages', 'Images')}
                      </div>
                    </div>
                  </div>

                  {/* Payment History Section */}
                  <div>
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-red-500" />
                      {t('adminDashboard.paymentHistory', 'Payment History')}
                    </h4>

                    {userDetail.payments && userDetail.payments.length > 0 ? (
                      <div className="space-y-2">
                        {userDetail.payments.map((payment: any) => (
                          <div
                            key={payment.id}
                            className="bg-black/40 border border-white/10 rounded-xl p-4"
                          >
                            <div className="flex items-start justify-between gap-4 mb-2">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span className="text-sm font-bold text-white font-mono">
                                    {payment.reference_code}
                                  </span>
                                  <span
                                    className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                                      payment.status === 'completed'
                                        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                        : payment.status === 'pending'
                                          ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                                          : payment.status === 'partial'
                                            ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                                            : 'bg-red-500/20 text-red-400 border border-red-500/30'
                                    }`}
                                  >
                                    {payment.status}
                                  </span>
                                </div>
                                <div className="text-xs text-white/40 mt-1">
                                  {new Date(payment.created_at).toLocaleString()}
                                </div>
                              </div>
                              <div className="text-right shrink-0">
                                <div className="text-sm font-bold text-white">
                                  {payment.received_amount} / {payment.expected_amount} EGP
                                </div>
                                <div className="text-[10px] text-white/40 uppercase tracking-wider">
                                  {payment.plan}
                                </div>
                              </div>
                            </div>
                            {/* Sender phone number */}
                            <div className="flex items-center gap-2 mt-2 pt-2 border-t border-white/5">
                              <span className="text-[10px] text-white/40 uppercase tracking-wider">
                                {t('adminDashboard.senderNumber', 'Sender Number')}:
                              </span>
                              <span className="text-sm text-white font-mono">
                                {payment.expected_sender_number || '—'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="bg-black/40 border border-white/10 rounded-xl p-6 text-center">
                        <p className="text-sm text-white/40">
                          {t('adminDashboard.noPayments', 'No payment records found.')}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Onboarding Section */}
                  <div>
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-red-500" />
                      {t('adminDashboard.onboardingAnswers', 'Onboarding Questionnaire')}
                    </h4>

                    {userDetail.onboarding ? (
                      <div className="bg-black/40 border border-white/10 rounded-xl divide-y divide-white/5">
                        <OnboardingRow
                          label={t('adminDashboard.businessName', 'Business Name')}
                          value={userDetail.onboarding.business_name}
                        />
                        <OnboardingRow
                          label={t('adminDashboard.governorate', 'Governorate')}
                          value={userDetail.onboarding.governorate}
                        />
                        <OnboardingRow
                          label={t('adminDashboard.businessType', 'Business Type')}
                          value={userDetail.onboarding.business_type}
                          other={userDetail.onboarding.business_type_other}
                        />
                        {userDetail.onboarding.business_subtype && (
                          <OnboardingRow
                            label={t('adminDashboard.businessSubtype', 'Business Subtype')}
                            value={userDetail.onboarding.business_subtype}
                          />
                        )}
                        <OnboardingRow
                          label={t('adminDashboard.marketingGoals', 'Marketing Goals')}
                          value={
                            Array.isArray(userDetail.onboarding.marketing_goals)
                              ? userDetail.onboarding.marketing_goals.join(', ')
                              : userDetail.onboarding.marketing_goals
                          }
                        />
                        <OnboardingRow
                          label={t('adminDashboard.targetAudience', 'Target Audience')}
                          value={userDetail.onboarding.target_audience}
                          other={userDetail.onboarding.target_audience_other}
                        />
                        <OnboardingRow
                          label={t('adminDashboard.toneOfVoice', 'Tone of Voice')}
                          value={userDetail.onboarding.tone_of_voice}
                          other={userDetail.onboarding.tone_of_voice_other}
                        />
                        {userDetail.onboarding.created_at && (
                          <OnboardingRow
                            label={t('adminDashboard.submittedOn', 'Submitted On')}
                            value={new Date(userDetail.onboarding.created_at).toLocaleString()}
                          />
                        )}
                      </div>
                    ) : (
                      <div className="bg-black/40 border border-white/10 rounded-xl p-6 text-center">
                        <p className="text-sm text-white/40">
                          {t(
                            'adminDashboard.noOnboarding',
                            'No onboarding questionnaire completed yet.'
                          )}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Helper component for onboarding rows
function OnboardingRow({
  label,
  value,
  other,
}: {
  label: string
  value: string | null | undefined
  other?: string | null | undefined
}) {
  const displayValue = value || (other ? null : '—')
  return (
    <div className="p-4 flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4">
      <div className="text-xs text-white/50 uppercase tracking-wider sm:w-48 shrink-0">{label}</div>
      <div className="text-sm text-white flex-1">
        {displayValue}
        {other && <span className="text-white/40 ml-2">({other})</span>}
      </div>
    </div>
  )
}
