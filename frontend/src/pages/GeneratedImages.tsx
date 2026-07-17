import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import DashboardLayout from '@/components/DashboardLayout'
import { useToast } from '@/hooks/use-toast'
import {
  Facebook,
  Edit3,
  Send,
  CheckCircle2,
  Loader2,
  MousePointerSquareDashed,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import api from '@/lib/axios'

export default function GeneratedImages() {
  const { t } = useTranslation()
  const [selectedPosts, setSelectedPosts] = useState<number[]>([])
  const [editingPost, setEditingPost] = useState<number | null>(null)
  const [modificationRequest, setModificationRequest] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toast } = useToast()

  const [mockPosts, setMockPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/images/mock-posts')
      .then((res) => {
        setMockPosts(res.data)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  const handleSelect = (id: number) => {
    setSelectedPosts((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]))
  }

  const handleRequestModification = (id: number | 'bulk') => {
    setIsSubmitting(true)
    setTimeout(() => {
      setIsSubmitting(false)
      setEditingPost(null)
      setModificationRequest('')
      toast({
        title: 'Modification Request Sent',
        description:
          id === 'bulk'
            ? `Request sent for ${selectedPosts.length} posts. Our team will review it shortly.`
            : `Request sent for post #${id}. Our team will update it shortly.`,
      })
      if (id === 'bulk') setSelectedPosts([])
    }, 1500)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6 pb-20">
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">{t('campaignPortfolio.title')}</h2>
            <p className="text-white/60">{t('campaignPortfolio.subtitle')}</p>
          </div>

          {selectedPosts.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-4 bg-white/10 px-4 py-2 rounded-lg border border-white/20 backdrop-blur-md"
            >
              <span className="text-sm font-medium text-white">
                {selectedPosts.length} {t('campaignPortfolio.selected')}
              </span>
              <Button
                size="sm"
                className="bg-vitamin-base hover:bg-vitamin-700 text-white"
                onClick={() => setEditingPost(999)} // 999 = bulk edit
              >
                <Edit3 className="h-4 w-4 mr-2" /> {t('campaignPortfolio.bulkEdit')}
              </Button>
            </motion.div>
          )}
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-white/50 gap-3">
            <Loader2 className="h-10 w-10 animate-spin text-vitamin-base" />
            <p>{t('campaignPortfolio.loading', 'Accessing campaign portfolio...')}</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            {mockPosts.map((post) => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: post.id * 0.1 }}
              >
                <Card
                  className={`glass-dark border transition-all duration-200 overflow-hidden ${
                    selectedPosts.includes(post.id)
                      ? 'border-vitamin-base ring-1 ring-vitamin-base'
                      : 'border-white/10 hover:border-white/30'
                  }`}
                >
                  <div className="relative aspect-video">
                    <img
                      src={post.previewDesign}
                      alt="Design Preview"
                      className="w-full h-full object-cover opacity-80"
                    />
                    <div className="absolute top-4 left-4">
                      <Badge
                        variant="secondary"
                        className="bg-black/50 text-white backdrop-blur-md border-none"
                      >
                        <Facebook className="w-3 h-3 mr-1 text-blue-400" /> {post.platform}
                      </Badge>
                    </div>
                    <div className="absolute top-4 right-4">
                      <button
                        onClick={() => handleSelect(post.id)}
                        className={`w-6 h-6 rounded-md flex items-center justify-center transition-colors ${
                          selectedPosts.includes(post.id)
                            ? 'bg-vitamin-base text-white'
                            : 'bg-black/50 text-white/50 hover:bg-black/70'
                        }`}
                      >
                        {selectedPosts.includes(post.id) ? (
                          <CheckCircle2 className="w-4 h-4" />
                        ) : (
                          <MousePointerSquareDashed className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  <CardContent className="p-6 space-y-4">
                    <div>
                      <h3 className="text-xl font-bold text-white">{post.title}</h3>
                      <p className="text-sm text-white/40 mt-1">Visual: {post.visualDirection}</p>
                    </div>

                    <div className="bg-white/5 p-4 rounded-lg border border-white/5">
                      <p className="text-white/80 text-sm leading-relaxed mb-3">"{post.caption}"</p>
                      <Badge variant="outline" className="text-vitamin-400 border-vitamin-400/30">
                        CTA: {post.cta}
                      </Badge>
                    </div>

                    {editingPost === post.id ? (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="space-y-3 pt-2 border-t border-white/10"
                      >
                        <label className="text-xs font-medium text-white/60 uppercase tracking-wider">
                          {t('campaignPortfolio.requestModification')}
                        </label>
                        <Textarea
                          placeholder="e.g. Make the colors darker, change the CTA to 'Learn More'..."
                          value={modificationRequest}
                          onChange={(e) => setModificationRequest(e.target.value)}
                          className="bg-white/5 border-white/10 text-white placeholder-white/30 resize-none"
                          rows={3}
                        />
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setEditingPost(null)}
                            className="text-white/60 hover:text-white"
                          >
                            {t('campaignPortfolio.cancel')}
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => handleRequestModification(post.id)}
                            disabled={!modificationRequest.trim() || isSubmitting}
                            className="bg-vitamin-base text-white"
                          >
                            {isSubmitting ? (
                              t('campaignPortfolio.sending')
                            ) : (
                              <>
                                <Send className="w-3 h-3 mr-2" />{' '}
                                {t('campaignPortfolio.sendRequest')}
                              </>
                            )}
                          </Button>
                        </div>
                      </motion.div>
                    ) : (
                      <div className="flex justify-end border-t border-white/10 pt-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-white/60 hover:text-white"
                          onClick={() => setEditingPost(post.id)}
                        >
                          <Edit3 className="w-4 h-4 mr-2" /> {t('campaignPortfolio.requestEdit')}
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
