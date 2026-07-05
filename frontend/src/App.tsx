import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom"
import { lazy, Suspense, useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import Navbar from "@/components/Navbar"
import { Toaster } from "@/components/ui/toaster"
import AdminProtectedRoute from "@/components/AdminProtectedRoute"
import { LoadingSpinner } from "@/components/LoadingSpinner"
import AnimatedBackground from "@/components/AnimatedBackground"
import Footer from "@/components/Footer"
import type { UsageResponse } from "@/types/api"
import api from "@/lib/axios"
import { getPremiumPosts } from "@/services/chatService"

const Landing = lazy(() => import("@/pages/Landing"))
const About = lazy(() => import("@/pages/About"))
const Work = lazy(() => import("@/pages/Work"))
const Login = lazy(() => import("@/pages/Login"))
const Register = lazy(() => import("@/pages/Register"))
const Pricing = lazy(() => import("@/pages/Pricing"))
const Dashboard = lazy(() => import("@/pages/Dashboard"))
const Support = lazy(() => import("@/pages/Support"))
const Subscription = lazy(() => import("@/pages/Subscription"))
const Contact = lazy(() => import("@/pages/Contact"))
const Chat = lazy(() => import("@/pages/Chat"))
const AdminDashboard = lazy(() => import("@/pages/AdminDashboard"))
const AdminLogin = lazy(() => import("@/pages/AdminLogin"))
const NewOnboarding = lazy(() => import("@/pages/NewOnboarding"))
const TeslaClients = lazy(() => import("@/pages/TeslaClients"))
const VodafoneCashPayment = lazy(() => import("@/pages/VodafoneCashPayment"))
const GeneratedImages = lazy(() => import("@/pages/GeneratedImages"))

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

/** Pro plan → Support. Basic plan or existing generated posts → Chat. */
function ChatRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  const [accessState, setAccessState] = useState<{
    usage: UsageResponse
    hasPosts: boolean
  } | null>(null)

  useEffect(() => {
    if (!isAuthenticated) return

    Promise.all([
      api.get<UsageResponse>("/users/usage"),
      getPremiumPosts().catch(() => ({ post_generation: null })),
    ])
      .then(([usageRes, postsData]) => {
        const hasPosts = Boolean(
          postsData.post_generation?.posts?.length
        )
        setAccessState({ usage: usageRes.data, hasPosts })
      })
      .catch(() =>
        setAccessState({
          usage: { has_access: false, plan_slug: null },
          hasPosts: false,
        })
      )
  }, [isAuthenticated])

  if (!isAuthenticated) return <Navigate to="/login" />
  if (accessState === null) return <LoadingSpinner />
  if (accessState.usage.plan_slug === "pro") return <Navigate to="/support" replace />
  if (!accessState.usage.has_access && !accessState.hasPosts) {
    return <Navigate to="/pricing" replace />
  }
  return <>{children}</>
}

function AppContent() {
  const { isAuthenticated, fetchProfile } = useAuthStore()
  const location = useLocation()

  useEffect(() => {
    if (isAuthenticated) {
      fetchProfile()
    }
  }, [isAuthenticated, fetchProfile])

  const isAdminPage = location.pathname === '/admin' || location.pathname === '/admin-login'

  return (
    <div className="min-h-screen flex flex-col relative text-white bg-black/40 dark:bg-black/60 transition-colors duration-1000">
      <AnimatedBackground />
      {!isAdminPage && <Navbar />}
      <main className="flex-grow flex flex-col relative z-10 w-full">
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/about" element={<About />} />
            <Route path="/work" element={<Work />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/new-onboarding"
              element={
                <ProtectedRoute>
                  <NewOnboarding />
                </ProtectedRoute>
              }
            />
            <Route path="/pricing" element={<Pricing />} />
            <Route
              path="/payment/vodafone-cash"
              element={
                <ProtectedRoute>
                  <VodafoneCashPayment />
                </ProtectedRoute>
              }
            />
            <Route path="/tesla-clients" element={<TeslaClients />} />
            <Route path="/contact" element={<Contact />} />
            <Route
              path="/chat"
              element={
                <ChatRoute>
                  <Chat />
                </ChatRoute>
              }
            />
            <Route path="/admin-login" element={<AdminLogin />} />
            <Route
              path="/admin"
              element={
                <AdminProtectedRoute>
                  <AdminDashboard />
                </AdminProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/support"
              element={
                <ProtectedRoute>
                  <Support />
                </ProtectedRoute>
              }
            />
            <Route
              path="/subscription"
              element={
                <ProtectedRoute>
                  <Subscription />
                </ProtectedRoute>
              }
            />
            <Route
              path="/generated-images"
              element={
                <ProtectedRoute>
                  <GeneratedImages />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Suspense>
      </main>
      <Footer />
      <Toaster />
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AppContent />
    </BrowserRouter>
  )
}
