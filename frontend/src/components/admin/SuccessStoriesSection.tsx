import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Edit, Trash2, Save, Loader2, FileText, Settings, Image as ImageIcon } from 'lucide-react'
import { api } from '@/lib/axios'

interface SuccessStory {
  id: number
  content_en: string
  content_ar: string
  video_url?: string
  is_active: boolean
  created_at: string
}

interface StorySettings {
  mode: 'auto' | 'manual'
  rotation_interval: number
  featured_video_id: number | null
}

export default function SuccessStoriesSection() {
  const { t } = useTranslation()
  const [successStories, setSuccessStories] = useState<SuccessStory[]>([])
  const [editingSuccessStory, setEditingSuccessStory] = useState<SuccessStory | null>(null)
  const [successStoryForm, setSuccessStoryForm] = useState({
    content_en: '',
    content_ar: '',
    video: null as File | null,
    is_active: true,
  })
  const [savingSuccessStory, setSavingSuccessStory] = useState(false)
  const [storySettings, setStorySettings] = useState<StorySettings>({
    mode: 'auto',
    rotation_interval: 24,
    featured_video_id: null,
  })
  const [savingSettings, setSavingSettings] = useState(false)

  const fetchSuccessStory = async () => {
    try {
      const response = await api.get('/portfolio/success-stories/all/')
      setSuccessStories(response.data)
    } catch (err) {
      console.error('Failed to fetch success stories:', err)
    }
  }

  const fetchStorySettings = async () => {
    try {
      const response = await api.get('/portfolio/success-story-settings/')
      if (response.data.length > 0) {
        setStorySettings({
          mode: response.data[0].mode,
          rotation_interval: response.data[0].rotation_interval,
          featured_video_id: response.data[0].featured_video?.id || null,
        })
      }
    } catch (err) {
      console.error('Failed to fetch story settings:', err)
    }
  }

  useEffect(() => {
    fetchSuccessStory()
    fetchStorySettings()
  }, [])

  const handleSaveSettings = async () => {
    setSavingSettings(true)
    try {
      const response = await api.get('/portfolio/success-story-settings/')
      const settingsData = {
        mode: storySettings.mode,
        rotation_interval: storySettings.rotation_interval,
        featured_video_id: storySettings.featured_video_id,
      }
      if (response.data.length > 0) {
        await api.put(`/portfolio/success-story-settings/${response.data[0].id}/`, settingsData)
      } else {
        await api.post('/portfolio/success-story-settings/', settingsData)
      }
      alert(t('adminDashboard.settingsSavedSuccess', 'Settings saved successfully!'))
      fetchStorySettings()
    } catch (err: any) {
      console.error('Failed to save settings:', err)
      alert(t('adminDashboard.failedSaveSettings', 'Failed to save settings.'))
    } finally {
      setSavingSettings(false)
    }
  }

  const handleSaveSuccessStory = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingSuccessStory(true)
    try {
      const formData = new FormData()
      formData.append('content_en', successStoryForm.content_en)
      formData.append('content_ar', successStoryForm.content_ar)
      formData.append('is_active', successStoryForm.is_active.toString())
      if (successStoryForm.video) {
        formData.append('video', successStoryForm.video)
      }

      if (editingSuccessStory) {
        await api.put(`/portfolio/success-stories/${editingSuccessStory.id}/`, formData)
        alert(t('adminDashboard.successStoryUpdatedSuccess'))
      } else {
        if (successStories.length >= 12) {
          alert('Maximum of 12 success stories allowed')
          setSavingSuccessStory(false)
          return
        }
        await api.post('/portfolio/success-stories/', formData)
        alert(t('adminDashboard.successStoryCreatedSuccess'))
      }
      setEditingSuccessStory(null)
      setSuccessStoryForm({
        content_en: '',
        content_ar: '',
        video: null,
        is_active: true,
      })
      fetchSuccessStory()
    } catch (err: any) {
      console.error('Failed to save success story', err)
      alert(err.response?.data?.detail || t('adminDashboard.failedSaveSuccessStory'))
    } finally {
      setSavingSuccessStory(false)
    }
  }

  const handleEditSuccessStory = (story: SuccessStory) => {
    setEditingSuccessStory(story)
    setSuccessStoryForm({
      content_en: story.content_en,
      content_ar: story.content_ar,
      video: null,
      is_active: story.is_active,
    })
  }

  const handleDeleteSuccessStory = async (id: number) => {
    if (
      !confirm(
        t(
          'adminDashboard.confirmDeleteProject',
          'Are you sure you want to delete this success story?'
        )
      )
    )
      return
    try {
      await api.delete(`/portfolio/success-stories/${id}/`)
      alert(t('adminDashboard.projectDeletedSuccess'))
      fetchSuccessStory()
    } catch (err: any) {
      console.error('Failed to delete success story', err)
      alert(t('adminDashboard.failedDeleteProject'))
    }
  }

  const handleCancelEditSuccessStory = () => {
    setEditingSuccessStory(null)
    setSuccessStoryForm({
      content_en: '',
      content_ar: '',
      video: null,
      is_active: true,
    })
  }

  return (
    <div className="space-y-8">
      {/* Settings Section */}
      <Card className="bg-black/45 border-red-500/20 backdrop-blur-md">
        <CardHeader className="border-b border-white/5 pb-4">
          <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-red-500" />
            {t('adminDashboard.displaySettings', 'Display Settings')}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">
                {t('adminDashboard.displayMode', 'Display Mode')}
              </label>
              <select
                value={storySettings.mode}
                onChange={(e) =>
                  setStorySettings({ ...storySettings, mode: e.target.value as 'auto' | 'manual' })
                }
                className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
              >
                <option value="auto">{t('adminDashboard.autoMode', 'Auto Mode')}</option>
                <option value="manual">{t('adminDashboard.manualMode', 'Manual Mode')}</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">
                {t('adminDashboard.rotationInterval', 'Rotation Interval (seconds)')}
              </label>
              <input
                type="number"
                min="5"
                max="300"
                value={storySettings.rotation_interval}
                onChange={(e) =>
                  setStorySettings({
                    ...storySettings,
                    rotation_interval: parseInt(e.target.value) || 24,
                  })
                }
                className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="mt-4">
            <Button
              onClick={handleSaveSettings}
              disabled={savingSettings}
              className="bg-red-600 hover:bg-red-700 text-white h-11 rounded-lg font-semibold"
            >
              {savingSettings ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {t('adminDashboard.saving')}
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {t('adminDashboard.saveSettings', 'Save Settings')}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Success Story Form */}
        <div className="lg:col-span-1">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md sticky top-[170px]">
            <CardHeader className="border-b border-white/5 pb-4">
              <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-red-500" />
                {editingSuccessStory
                  ? t('adminDashboard.editSuccessStory', 'Edit Success Story')
                  : t('adminDashboard.addSuccessStory', 'Add Success Story')}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleSaveSuccessStory} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">
                    {t('adminDashboard.contentEn', 'Content (English)')}
                  </label>
                  <textarea
                    required
                    value={successStoryForm.content_en}
                    onChange={(e) =>
                      setSuccessStoryForm({ ...successStoryForm, content_en: e.target.value })
                    }
                    placeholder="Enter the success story content in English..."
                    rows={6}
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none resize-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">
                    {t('adminDashboard.contentAr', 'Content (Arabic)')}
                  </label>
                  <textarea
                    required
                    value={successStoryForm.content_ar}
                    onChange={(e) =>
                      setSuccessStoryForm({ ...successStoryForm, content_ar: e.target.value })
                    }
                    placeholder="أدخل محتوى قصة النجاح باللغة العربية..."
                    rows={6}
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none resize-none"
                    dir="rtl"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">
                    {t('adminDashboard.video', 'Video File')}
                  </label>
                  <input
                    type="file"
                    accept="video/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0] || null
                      if (file && file.name.length > 100) {
                        alert('Filename is too long (max 100 characters). Please rename the file.')
                        e.target.value = ''
                        return
                      }
                      setSuccessStoryForm({ ...successStoryForm, video: file })
                    }}
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                  {editingSuccessStory?.video_url && !successStoryForm.video && (
                    <p className="text-xs text-white/40 mt-1">
                      {t('adminDashboard.currentVideo', 'Current video:')}{' '}
                      {editingSuccessStory.video_url}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="success_story_active"
                    checked={successStoryForm.is_active}
                    onChange={(e) =>
                      setSuccessStoryForm({ ...successStoryForm, is_active: e.target.checked })
                    }
                    className="w-4 h-4 bg-black/40 border border-white/10 rounded focus:border-red-500 focus:outline-none"
                  />
                  <label htmlFor="success_story_active" className="text-xs text-white/60">
                    {t('adminDashboard.active')}
                  </label>
                </div>

                <div className="flex gap-2">
                  <Button
                    type="submit"
                    disabled={savingSuccessStory}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white h-11 rounded-lg font-semibold"
                  >
                    {savingSuccessStory ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {t('adminDashboard.saving')}
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        {editingSuccessStory
                          ? t('adminDashboard.update')
                          : t('adminDashboard.create')}
                      </>
                    )}
                  </Button>
                  {editingSuccessStory && (
                    <Button
                      type="button"
                      onClick={handleCancelEditSuccessStory}
                      variant="outline"
                      className="border-white/20 text-white hover:bg-white/10 h-11 rounded-lg"
                    >
                      {t('adminDashboard.cancel')}
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Success Stories List */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md overflow-hidden">
            <CardHeader className="border-b border-white/5 p-5">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                  <FileText className="w-5 h-5 text-red-500" />
                  {t('adminDashboard.allSuccessStories', 'All Success Stories')}
                </CardTitle>
                <Badge className="bg-red-500/20 border-red-500/30 text-red-400">
                  {successStories.length}/12
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5 bg-white/5 text-white/50 text-left font-semibold">
                      {storySettings.mode === 'manual' && (
                        <th className="p-4">{t('adminDashboard.featured', 'Featured')}</th>
                      )}
                      <th className="p-4">{t('adminDashboard.contentEn')}</th>
                      <th className="p-4">{t('adminDashboard.video')}</th>
                      <th className="p-4">{t('adminDashboard.status')}</th>
                      <th className="p-4 text-right">{t('adminDashboard.actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {successStories.map((story) => (
                      <tr
                        key={story.id}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        {storySettings.mode === 'manual' && (
                          <td className="p-4">
                            <input
                              type="radio"
                              name="featured_video"
                              checked={storySettings.featured_video_id === story.id}
                              onChange={() =>
                                setStorySettings({ ...storySettings, featured_video_id: story.id })
                              }
                              className="w-4 h-4 bg-black/40 border border-white/10 rounded focus:border-red-500 focus:outline-none"
                            />
                          </td>
                        )}
                        <td className="p-4">
                          <div className="font-bold text-white line-clamp-2 max-w-[300px]">
                            {story.content_en}
                          </div>
                          <div className="text-xs text-white/40 mt-1">
                            {new Date(story.created_at).toLocaleDateString()}
                          </div>
                        </td>
                        <td className="p-4">
                          {story.video_url ? (
                            <div className="flex items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-8 border-white/20 text-white hover:bg-white/10"
                              >
                                <ImageIcon className="w-3.5 h-3.5 mr-1" />
                                {t('adminDashboard.preview', 'Preview')}
                              </Button>
                            </div>
                          ) : (
                            <span className="text-white/40 text-xs">
                              {t('adminDashboard.noVideo', 'No video')}
                            </span>
                          )}
                        </td>
                        <td className="p-4">
                          <Badge
                            className={
                              story.is_active
                                ? 'bg-green-500/20 border-green-500/30 text-green-400'
                                : 'bg-red-500/20 border-red-500/30 text-red-400'
                            }
                          >
                            {story.is_active
                              ? t('adminDashboard.active')
                              : t('adminDashboard.inactive')}
                          </Badge>
                        </td>
                        <td className="p-4 text-right flex items-center justify-end gap-2">
                          <Button
                            onClick={() => handleEditSuccessStory(story)}
                            variant="outline"
                            size="sm"
                            className="h-8 border-red-500/35 hover:bg-red-500/10 text-red-400 font-semibold"
                          >
                            <Edit className="w-3.5 h-3.5 mr-1" />
                            {t('adminDashboard.edit')}
                          </Button>
                          <Button
                            onClick={() => handleDeleteSuccessStory(story.id)}
                            variant="ghost"
                            size="sm"
                            className="h-8 text-white/40 hover:text-red-500 hover:bg-red-500/10"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {successStories.length === 0 && (
                      <tr>
                        <td
                          colSpan={storySettings.mode === 'manual' ? 5 : 4}
                          className="p-12 text-center text-white/40"
                        >
                          {t('adminDashboard.noSuccessStory', 'No success stories created yet')}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
