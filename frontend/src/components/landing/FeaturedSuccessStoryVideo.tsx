import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'
import api from '@/lib/axios'

interface FeaturedStory {
  id: number
  content_en: string
  content_ar: string
  video_url: string | null
  is_active: boolean
}

interface StorySettings {
  mode: 'auto' | 'manual'
  rotation_interval: number
  featured_video: number | null
}

/**
 * Renders the featured Success Story video selected in the Admin Dashboard.
 *
 * Logic:
 * - If mode='manual' and a featured_video is set, show that specific story.
 * - If mode='auto' (or no settings), show the first active story with a video.
 * - If no stories exist or none have videos, render nothing.
 */
export function FeaturedSuccessStoryVideo() {
  const { t, i18n } = useTranslation()
  const [story, setStory] = useState<FeaturedStory | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFeatured = async () => {
      try {
        const [storiesRes, settingsRes] = await Promise.all([
          api.get('/portfolio/success-stories/'),
          api.get('/portfolio/success-story-settings/'),
        ])

        const stories: FeaturedStory[] = storiesRes.data || []
        const settingsRow =
          Array.isArray(settingsRes.data) && settingsRes.data.length > 0
            ? settingsRes.data[0]
            : null
        const settings: StorySettings = {
          mode: settingsRow?.mode || 'auto',
          rotation_interval: Number(settingsRow?.rotation_interval) || 24,
          featured_video: settingsRow?.featured_video || null,
        }

        // Manual mode: find the featured story by ID
        if (settings.mode === 'manual' && settings.featured_video) {
          const featured = stories.find((s) => s.id === settings.featured_video)
          if (featured && featured.video_url) {
            setStory(featured)
            return
          }
        }

        // Auto mode or no featured video: pick the first active story with a video
        const firstWithVideo = stories.find((s) => s.is_active && s.video_url)
        if (firstWithVideo) {
          setStory(firstWithVideo)
        }
      } catch (error) {
        console.error('Failed to fetch featured success story:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchFeatured()
  }, [])

  // Don't render anything while loading or if no story with video exists
  if (loading || !story || !story.video_url) {
    return null
  }

  return (
    <section className="relative py-32 px-4 border-t border-white/5 bg-black/20 dark:bg-black/40 backdrop-blur-sm transition-colors duration-1000">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-5xl font-cinematic font-bold mb-4 text-white transition-colors">
            {t('work.successStoryTitle', 'Success Stories')}
          </h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="relative rounded-3xl overflow-hidden border border-white/10 bg-black/40"
        >
          <video
            key={story.id}
            src={story.video_url}
            controls
            autoPlay={false}
            className="w-full aspect-video object-cover"
          />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-xl text-white/70 leading-relaxed mt-8 text-center max-w-3xl mx-auto"
        >
          {i18n.language === 'ar' ? story.content_ar : story.content_en}
        </motion.p>
      </div>
    </section>
  )
}
