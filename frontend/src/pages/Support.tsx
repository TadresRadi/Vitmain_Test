import { useState, useEffect, useRef } from "react"
import { useTranslation } from "react-i18next"
import DashboardLayout from "@/components/DashboardLayout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Send, Loader2, MessageSquare, Shield } from "lucide-react"
import api from "@/lib/axios"
import { useToast } from "@/hooks/use-toast"
import { motion } from "framer-motion"

interface SupportMessage {
  id: number
  sender_email: string
  sender_name: string
  sender_role: string
  content: string
  created_at: string
}

interface SupportChat {
  id: string
  user_email: string
  user_name: string
  messages: SupportMessage[]
}

export default function Support() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [chat, setChat] = useState<SupportChat | null>(null)
  const [newMessage, setNewMessage] = useState("")
  const [sending, setSending] = useState(false)
  const [loading, setLoading] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // User details form state
  const [userDetailsSubmitted, setUserDetailsSubmitted] = useState(false)
  const [userDetails, setUserDetails] = useState({
    fullName: "",
    businessName: "",
    phoneNumber: ""
  })
  const [submittingDetails, setSubmittingDetails] = useState(false)

  // Handle user details submission
  const handleUserDetailsSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!userDetails.fullName.trim() || !userDetails.businessName.trim() || !userDetails.phoneNumber.trim()) {
      toast({
        title: t("common.error", "Error"),
        description: "Please fill in all fields.",
        variant: "destructive",
      })
      return
    }

    setSubmittingDetails(true)
    try {
      // Submit user details as the first message to create a support conversation
      const detailsMessage = `New Support Request\n\nFull Name: ${userDetails.fullName}\nBusiness Name: ${userDetails.businessName}\nPhone Number: ${userDetails.phoneNumber}`
      await api.post("/support/chat", { content: detailsMessage })
      setUserDetailsSubmitted(true)
      toast({
        title: t("support.detailsSubmitted", "Details Submitted Successfully"),
        description: t("support.detailsSubmittedDesc", "Thank you! You can now use the support chat."),
      })
      // Now fetch the chat
      fetchChat()
    } catch (err) {
      console.error("Failed to submit user details:", err)
      toast({
        title: t("common.error", "Error"),
        description: "Failed to submit details. Please try again.",
        variant: "destructive",
      })
    } finally {
      setSubmittingDetails(false)
    }
  }

  // Fetch support chat on mount
  const fetchChat = async () => {
    try {
      const response = await api.get("/support/chat")
      setChat(response.data)
    } catch (err) {
      console.error("Failed to fetch support chat:", err)
      toast({
        title: t("common.error", "Error"),
        description: t("support.loadError", "Could not load support ticket. Please try again."),
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Only fetch chat if user details have been submitted
    if (userDetailsSubmitted) {
      fetchChat()
      // Poll for new messages every 5 seconds to simulate real-time chat
      const interval = setInterval(fetchChat, 5000)
      return () => clearInterval(interval)
    }
  }, [userDetailsSubmitted])

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [chat?.messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim() || sending) return

    setSending(true)
    try {
      const response = await api.post("/support/chat", { content: newMessage })
      // Append the new message locally immediately
      if (chat) {
        setChat({
          ...chat,
          messages: [...chat.messages, response.data]
        })
      }
      setNewMessage("")
    } catch (err) {
      console.error("Failed to send message:", err)
      toast({
        title: t("common.error", "Error"),
        description: t("support.sendError", "Could not send message. Please try again."),
        variant: "destructive",
      })
    } finally {
      setSending(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto h-[calc(100vh-12rem)] flex flex-col relative z-10">
        
        {/* Support Header */}
        <Card className="glass-dark border-white/20 p-4 mb-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-vitamin-base/20 border border-vitamin-base/30 flex items-center justify-center">
              <MessageSquare className="h-5 w-5 text-vitamin-base animate-pulse" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Vitamin Support Hub
              </h2>
              <p className="text-white/60 text-xs">
                Speak directly with our brand advisors and technical team.
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            Admins Online
          </div>
        </Card>

        {/* User Details Form - Show before chat */}
        {!userDetailsSubmitted ? (
          <Card className="glass-dark border-white/20 p-8 flex-1 flex flex-col items-center justify-center shadow-2xl backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="w-full max-w-md"
            >
              <div className="text-center mb-6">
                <div className="w-16 h-16 rounded-full bg-vitamin-base/20 border border-vitamin-base/30 flex items-center justify-center mx-auto mb-4">
                  <MessageSquare className="h-8 w-8 text-vitamin-base" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{t("support.userDetailsRequired", "User Details Required")}</h3>
                <p className="text-sm text-white/60">{t("support.userDetailsRequiredDesc", "Please provide your contact information to ensure proper communication and full support follow-up.")}</p>
              </div>

              <form onSubmit={handleUserDetailsSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">{t("support.fullName", "Full Name")}</label>
                  <Input
                    value={userDetails.fullName}
                    onChange={(e) => setUserDetails(prev => ({ ...prev, fullName: e.target.value }))}
                    placeholder={t("support.fullName", "Full Name")}
                    required
                    className="bg-slate-950 border border-white/20 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base rounded-xl h-12"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">{t("support.businessName", "Business Name")}</label>
                  <Input
                    value={userDetails.businessName}
                    onChange={(e) => setUserDetails(prev => ({ ...prev, businessName: e.target.value }))}
                    placeholder={t("support.businessName", "Business Name")}
                    required
                    className="bg-slate-950 border border-white/20 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base rounded-xl h-12"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">{t("support.phoneNumber", "Phone Number")}</label>
                  <Input
                    value={userDetails.phoneNumber}
                    onChange={(e) => setUserDetails(prev => ({ ...prev, phoneNumber: e.target.value }))}
                    placeholder={t("support.phoneNumber", "Phone Number")}
                    required
                    className="bg-slate-950 border border-white/20 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base rounded-xl h-12"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={submittingDetails}
                  className="w-full bg-gradient-to-r from-vitamin-base to-purple-600 hover:from-vitamin-700 hover:to-purple-700 text-white rounded-xl h-12 flex items-center justify-center transition-all duration-300"
                >
                  {submittingDetails ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin mr-2" />
                      {t("common.loading", "Loading...")}
                    </>
                  ) : (
                    t("support.submitDetails", "Submit Details")
                  )}
                </Button>
              </form>
            </motion.div>
          </Card>
        ) : (
          <>
            {/* Chat History Area */}
            <Card className="glass-dark border-white/20 flex-1 p-6 overflow-y-auto mb-4 flex flex-col gap-4 max-h-[calc(100vh-22rem)] shadow-2xl backdrop-blur-md">
              {loading ? (
                <div className="flex-1 flex flex-col items-center justify-center text-white/55 gap-3">
                  <Loader2 className="h-8 w-8 animate-spin text-vitamin-base" />
                  <span>Loading conversation history...</span>
                </div>
              ) : chat && chat.messages.length > 0 ? (
                chat.messages.map((message) => {
                  const isAdmin = message.sender_role === "super_admin" || message.sender_role === "supervisor"
                  return (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex flex-col max-w-[80%] ${isAdmin ? "self-start" : "self-end items-end"}`}
                    >
                      <div className="flex items-center gap-1.5 mb-1 px-1 text-white/50 text-[10px] font-semibold">
                        {isAdmin && <Shield className="h-3 w-3 text-vitamin-base shrink-0" />}
                        <span>{isAdmin ? message.sender_name || "Support Advisor" : "You"}</span>
                        <span>•</span>
                        <span>{new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                      <div
                        className={`rounded-2xl px-4 py-2.5 text-sm font-medium shadow-md leading-relaxed whitespace-pre-wrap ${
                          isAdmin
                            ? "bg-slate-900 border border-white/10 text-white/95 rounded-tl-none"
                            : "bg-gradient-to-r from-vitamin-base to-purple-600 text-white rounded-tr-none shadow-vitamin-base/10"
                        }`}
                      >
                        {message.content}
                      </div>
                    </motion.div>
                  )
                })
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-white/50 text-center p-6 gap-2">
                  <MessageSquare className="h-12 w-12 text-white/20 mb-2" />
                  <h3 className="font-bold text-white text-lg">No Messages Yet</h3>
                  <p className="text-sm max-w-sm">
                    Type a message below to start a ticket. Our support team responds quickly.
                  </p>
                </div>
              )}
              <div ref={messagesEndRef} />
            </Card>

            {/* Chat Input form */}
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <Input
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your question or request..."
                required
                className="flex-1 bg-slate-950 border border-white/20 text-white placeholder-white/40 focus:border-vitamin-base focus:ring-1 focus:ring-vitamin-base rounded-xl h-12"
              />
              <Button
                type="submit"
                disabled={sending || !newMessage.trim()}
                className="bg-gradient-to-r from-vitamin-base to-purple-600 hover:from-vitamin-700 hover:to-purple-700 text-white rounded-xl px-6 h-12 flex items-center justify-center transition-all duration-300"
              >
                {sending ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
              </Button>
            </form>
          </>
        )}

      </div>
    </DashboardLayout>
  )
}
