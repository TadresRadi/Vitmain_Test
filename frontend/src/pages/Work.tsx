import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'
import { useEffect, useState, useRef } from 'react'
import api from '../lib/axios'

interface Project {
  id: number
  title: string
  description: string
  category: string
  image_url: string
  order: number
  is_active: boolean
}

interface SuccessStory {
  id: number
  content_en: string
  content_ar: string
  video_url: string
  is_active: boolean
}

export default function Work() {
  const { t, i18n } = useTranslation()
  const [projects, setProjects] = useState<Project[]>([])
  const [successStories, setSuccessStories] = useState<SuccessStory[]>([])
  const [currentStoryIndex, setCurrentStoryIndex] = useState(0)
  const [storySettings, setStorySettings] = useState({
    mode: 'auto',
    interval: 24,
    featured_video_id: null as number | null,
  })
  const [loading, setLoading] = useState(true)
  const [dataLoaded, setDataLoaded] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectsRes, successStoryRes, settingsRes] = await Promise.all([
          api.get('/portfolio/projects/'),
          api.get('/portfolio/success-stories/'),
          api.get('/portfolio/success-story-settings/'),
        ])
        setProjects(projectsRes.data)
        setSuccessStories(successStoryRes.data)

        // Use the first settings row if it exists, otherwise use defaults.
        // Always set dataLoaded=true so the story section can render even
        // when the admin hasn't configured settings yet.
        const settingsRow =
          Array.isArray(settingsRes.data) && settingsRes.data.length > 0
            ? settingsRes.data[0]
            : null

        setStorySettings({
          mode: settingsRow?.mode || 'auto',
          interval: Number(settingsRow?.rotation_interval) || 24,
          featured_video_id: settingsRow?.featured_video || null,
        })
        setDataLoaded(true)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const intervalRef = useRef<number | null>(null)

  // Initialize current story index based on mode and settings
  useEffect(() => {
    if (!dataLoaded || successStories.length === 0) return

    if (storySettings.mode === 'manual' && storySettings.featured_video_id) {
      // Find the index of the featured video
      const featuredIndex = successStories.findIndex(
        (s) => s.id === Number(storySettings.featured_video_id)
      )
      if (featuredIndex !== -1) {
        setCurrentStoryIndex(featuredIndex)
      } else {
        // If featured video not found in stories, default to first
        setCurrentStoryIndex(0)
      }
    } else {
      // For auto mode or no featured video, start with first story
      setCurrentStoryIndex(0)
    }
  }, [dataLoaded, successStories, storySettings.mode, storySettings.featured_video_id])

  // Auto-rotate stories based on backend settings
  useEffect(() => {
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    // Only start interval if stories exist
    if (successStories.length === 0) return

    // Set new interval - always runs regardless of mode
    intervalRef.current = setInterval(
      () => {
        setCurrentStoryIndex((currentIndex) => {
          if (successStories.length === 0) return 0
          if (successStories.length === 1) return 0

          if (storySettings.mode === 'manual' && storySettings.featured_video_id) {
            // In manual mode, exclude current video from random selection
            const availableIndices = successStories
              .map((_, index) => index)
              .filter((index) => index !== currentIndex)
            const randomIndex =
              availableIndices[Math.floor(Math.random() * availableIndices.length)]
            return randomIndex
          } else {
            // In auto mode, select from all videos randomly
            const randomIndex = Math.floor(Math.random() * successStories.length)
            return randomIndex
          }
        })
      },
      Math.max(5, storySettings.interval) * 1000
    )

    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [successStories, storySettings.mode, storySettings.interval, storySettings.featured_video_id])

  if (loading) {
    return (
      <div className="relative z-10 pt-32 pb-20 px-4 min-h-screen">
        <div className="max-w-7xl mx-auto flex items-center justify-center">
          <div className="text-white/50">Loading...</div>
        </div>
      </div>
    )
  }

  const currentStory = successStories[currentStoryIndex]

  return (
    <div className="relative z-10 pt-32 pb-20 px-4 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-20"
        >
          <h1 className="text-5xl md:text-7xl font-cinematic font-bold text-white mb-6">
            {t('work.title')} <span className="text-vitamin-base">{t('work.titleHighlight')}</span>
          </h1>
          <p className="text-xl text-white/70 max-w-2xl mx-auto">{t('work.heroDesc')}</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.isArray(projects) &&
            projects.map((project, i) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                className="relative group cursor-pointer overflow-hidden rounded-2xl"
              >
                <img
                  src={project.image_url}
                  alt={project.title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 opacity-80 group-hover:opacity-100"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-80" />

                <div className="absolute inset-0 p-8 flex flex-col justify-end transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                  <span className="text-vitamin-base font-medium tracking-wider uppercase text-sm mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-500 delay-100">
                    {project.category}
                  </span>
                  <h3 className="text-3xl font-bold text-white">{project.title}</h3>
                </div>
              </motion.div>
            ))}
        </div>

        {/* Success Story Section */}
        {successStories.length > 0 && currentStory && currentStory.is_active && (
          <motion.div
            key={currentStory.id}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mt-32"
          >
            <div className="text-center mb-12">
              <h2 className="text-5xl font-cinematic font-bold text-white mb-4">
                {t('work.successStoryTitle')}
              </h2>
            </div>

            <div className="max-w-4xl mx-auto">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="glass-dark border border-white/10 rounded-3xl p-8 md:p-12 mb-8"
              >
                <p className="text-xl text-white/80 leading-relaxed whitespace-pre-line">
                  {i18n.language === 'ar' ? currentStory.content_ar : currentStory.content_en}
                </p>
              </motion.div>

              {currentStory.video_url && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="relative rounded-3xl overflow-hidden border border-white/10"
                >
                  <video
                    key={currentStory.id}
                    src={currentStory.video_url}
                    controls
                    className="w-full aspect-video"
                  />
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
