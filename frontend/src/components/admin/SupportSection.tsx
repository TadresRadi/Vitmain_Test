import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageSquare, User, Mail, Phone, Send } from "lucide-react"
import { adminApi } from "@/lib/axios"
import { useAdminAuthStore } from "@/store/adminAuthStore"

interface Conversation {
  id: number
  user_name?: string
  user_email: string
  user_phone?: string
  created_at: string
  messages: Array<{
    id: number
    content: string
    sender_email?: string
    sender_name?: string
    sender?: number
    created_at: string
  }>
}

export default function SupportSection() {
  const { t } = useTranslation()
  const { adminUser } = useAdminAuthStore()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [chatMessage, setChatMessage] = useState('')

  const fetchConversations = async () => {
    try {
      const response = await adminApi.get('/admin/support/chats')
      setConversations(response.data)
    } catch (err) {
      console.error("Failed to fetch conversations:", err)
    }
  }

  useEffect(() => {
    fetchConversations()
  }, [])

  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !selectedConversation) return

    try {
      await adminApi.post('/admin/support/reply', {
        conversation_id: selectedConversation.id,
        content: chatMessage
      })
      setChatMessage('')
      fetchConversations()
    } catch (err) {
      console.error("Failed to send message:", err)
      alert("Failed to send message")
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Conversations Column */}
        <Card className="bg-black/45 border-red-500/20 backdrop-blur-md lg:col-span-1 overflow-hidden h-[680px] flex flex-col">
          <CardHeader className="border-b border-white/5 p-4 bg-white/5">
            <CardTitle className="text-base font-bold text-white flex items-center gap-2">
              <MessageSquare className="w-4.5 h-4.5 text-red-500" />
              {t('adminDashboard.supportRooms', "Active Support Conversations")}
            </CardTitle>
          </CardHeader>
          <ScrollArea className="flex-1">
            <div className="p-3 space-y-2">
              {conversations.length === 0 ? (
                <div className="py-20 text-center text-white/40 text-xs">
                  {t('adminDashboard.noRooms', "No active support chat rooms.")}
                </div>
              ) : (
                conversations.map((conv) => {
                  const lastMsg = conv.messages?.[conv.messages.length - 1]
                  const isSelected = selectedConversation?.id === conv.id
                  
                  return (
                    <button
                      key={conv.id}
                      onClick={() => setSelectedConversation(conv)}
                      className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                        isSelected
                          ? 'bg-red-500/10 border-red-500/35 shadow-lg shadow-red-500/5'
                          : 'bg-black/20 border-white/5 hover:border-white/10'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-sm text-white truncate max-w-[160px]">
                          {conv.user_name || conv.user_email}
                        </span>
                        <span className="text-[10px] text-white/30 font-mono">
                          {new Date(conv.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <p className="text-xs text-white/50 truncate mt-1.5 leading-relaxed font-sans">
                        {lastMsg ? lastMsg.content : "Room opened"}
                      </p>
                    </button>
                  )
                })
              )}
            </div>
          </ScrollArea>
        </Card>

        {/* Chat Window Column */}
        <Card className="bg-black/45 border-red-500/20 backdrop-blur-md lg:col-span-2 h-[680px] flex flex-col overflow-hidden">
          {selectedConversation ? (
            <div className="flex-grow flex flex-col h-full overflow-hidden">
              
              {/* Active Chat Header with User details */}
              <div className="p-4 border-b border-white/5 bg-white/5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="font-bold text-sm text-white flex items-center gap-1.5">
                    <User className="w-4 h-4 text-red-500" />
                    {selectedConversation.user_name || "Anonymous User"}
                  </h3>
                  <p className="text-xs text-white/40 mt-0.5">{selectedConversation.user_email}</p>
                </div>
                
                {/* USER PROFILE INFO BOX CARD FOR CONSOLE */}
                <div className="bg-black/35 border border-white/10 rounded-lg p-2.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-white/60 backdrop-blur-sm max-w-lg">
                  <span className="flex items-center gap-1">
                    <Mail className="w-3.5 h-3.5 text-red-500" />
                    {selectedConversation.user_email}
                  </span>
                  {selectedConversation.user_phone && (
                    <span className="flex items-center gap-1">
                      <Phone className="w-3.5 h-3.5 text-red-500" />
                      {selectedConversation.user_phone}
                    </span>
                  )}
                </div>
              </div>

              {/* Chat Messages */}
              <div className="flex-grow overflow-y-auto p-6 space-y-4">
                {selectedConversation.messages.map((msg) => {
                  const isAdminSender = msg.sender_email === 'support@vitmain.com' || msg.sender_name === 'Vitmain Support' || msg.sender === adminUser?.id
                  
                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isAdminSender ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className="max-w-[75%] space-y-1">
                        <div className={`p-3.5 rounded-2xl text-sm leading-relaxed ${
                          isAdminSender
                            ? 'bg-red-600 text-white rounded-tr-none shadow-md shadow-red-600/10'
                            : 'bg-white/10 text-white border border-white/15 rounded-tl-none backdrop-blur-md'
                        }`}>
                          {msg.content}
                        </div>
                        <div className={`text-[10px] text-white/30 px-1 ${isAdminSender ? 'text-right' : 'text-left'}`}>
                          {msg.sender_name || msg.sender_email || "System"} • {new Date(msg.created_at).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Chat Input */}
              <div className="p-4 border-t border-white/5 bg-black/45 backdrop-blur-sm">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder={t('adminDashboard.typeReply', "Type supervisor/admin message reply...")}
                    className="flex-grow bg-black/40 border border-white/10 text-white rounded-xl px-4 py-3 text-sm focus:border-red-500 focus:outline-none placeholder-white/20"
                  />
                  <Button 
                    onClick={handleSendMessage} 
                    disabled={!chatMessage.trim()}
                    className="bg-red-600 hover:bg-red-700 text-white h-11 w-11 rounded-xl shrink-0 flex items-center justify-center"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center text-white/40 p-6 space-y-3">
              <MessageSquare className="w-12 h-12 text-white/25 animate-pulse" />
              <p className="text-sm font-medium">{t('adminDashboard.selectRoom', "Select a chat room on the left to start replying.")}</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
