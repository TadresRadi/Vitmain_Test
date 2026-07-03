import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Plus, Edit, Trash2, Save, Loader2, Star } from "lucide-react"
import { adminApi } from "@/lib/axios"

interface FeaturedProject {
  id: number
  title: string
  description: string
  category: string
  image_url?: string
  order: number
  is_active: boolean
}

interface FeaturedProjectsSectionProps {
  // Add any props if needed
}

export default function FeaturedProjectsSection({}: FeaturedProjectsSectionProps) {
  const { t } = useTranslation()
  const [featuredProjects, setFeaturedProjects] = useState<FeaturedProject[]>([])
  const [editingFeaturedProject, setEditingFeaturedProject] = useState<FeaturedProject | null>(null)
  const [featuredProjectForm, setFeaturedProjectForm] = useState({
    title: '',
    description: '',
    category: '',
    image: null as File | null,
    order: 0,
    is_active: true
  })
  const [savingFeaturedProject, setSavingFeaturedProject] = useState(false)

  const fetchFeaturedProjects = async () => {
    try {
      const res = await adminApi.get("/portfolio/featured-projects/all/")
      setFeaturedProjects(res.data)
    } catch (err: any) {
      console.error('Failed to fetch featured projects:', err)
    }
  }

  useEffect(() => {
    fetchFeaturedProjects()
  }, [])

  const handleSaveFeaturedProject = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingFeaturedProject(true)
    try {
      const formData = new FormData()
      formData.append('title', featuredProjectForm.title)
      formData.append('description', featuredProjectForm.description)
      formData.append('category', featuredProjectForm.category)
      formData.append('order', featuredProjectForm.order.toString())
      formData.append('is_active', featuredProjectForm.is_active.toString())
      if (featuredProjectForm.image) {
        formData.append('image', featuredProjectForm.image)
      }

      if (editingFeaturedProject) {
        await adminApi.put(`/portfolio/featured-projects/${editingFeaturedProject.id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        alert(t('adminDashboard.projectUpdatedSuccess'))
      } else {
        await adminApi.post('/portfolio/featured-projects/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        alert(t('adminDashboard.projectCreatedSuccess'))
      }
      setEditingFeaturedProject(null)
      setFeaturedProjectForm({
        title: '',
        description: '',
        category: '',
        image: null,
        order: 0,
        is_active: true
      })
      fetchFeaturedProjects()
    } catch (err: any) {
      console.error("Failed to save featured project", err)
      alert(err.response?.data?.detail || t('adminDashboard.failedSaveProject'))
    } finally {
      setSavingFeaturedProject(false)
    }
  }

  const handleEditFeaturedProject = (project: FeaturedProject) => {
    setEditingFeaturedProject(project)
    setFeaturedProjectForm({
      title: project.title,
      description: project.description,
      category: project.category,
      image: null,
      order: project.order,
      is_active: project.is_active
    })
  }

  const handleDeleteFeaturedProject = async (projectId: number) => {
    if (!confirm(t('adminDashboard.confirmDeleteProject'))) return
    try {
      await adminApi.delete(`/portfolio/featured-projects/${projectId}/`)
      alert(t('adminDashboard.projectDeletedSuccess'))
      fetchFeaturedProjects()
    } catch (err: any) {
      console.error("Failed to delete featured project", err)
      let errorMessage = t('adminDashboard.failedDeleteProject', 'Failed to delete project')
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      }
      alert(errorMessage)
    }
  }

  const handleCancelEditFeaturedProject = () => {
    setEditingFeaturedProject(null)
    setFeaturedProjectForm({
      title: '',
      description: '',
      category: '',
      image: null,
      order: 0,
      is_active: true
    })
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Featured Project Form */}
        <div className="lg:col-span-1">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md sticky top-[170px]">
            <CardHeader className="border-b border-white/5 pb-4">
              <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                <Plus className="w-5 h-5 text-red-500" />
                {editingFeaturedProject ? t('adminDashboard.editFeaturedProject') : t('adminDashboard.addNewFeaturedProject')}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleSaveFeaturedProject} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.title')}</label>
                  <input
                    type="text"
                    required
                    value={featuredProjectForm.title}
                    onChange={(e) => setFeaturedProjectForm({ ...featuredProjectForm, title: e.target.value })}
                    placeholder="Project title"
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.category')}</label>
                  <input
                    type="text"
                    required
                    value={featuredProjectForm.category}
                    onChange={(e) => setFeaturedProjectForm({ ...featuredProjectForm, category: e.target.value })}
                    placeholder="e.g. Web Design, Branding"
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.description')}</label>
                  <textarea
                    required
                    value={featuredProjectForm.description}
                    onChange={(e) => setFeaturedProjectForm({ ...featuredProjectForm, description: e.target.value })}
                    placeholder="Project description"
                    rows={3}
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none resize-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.image')}</label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0] || null
                      if (file && file.name.length > 100) {
                        alert('Filename is too long (max 100 characters). Please rename the file.')
                        e.target.value = ''
                        return
                      }
                      setFeaturedProjectForm({ ...featuredProjectForm, image: file })
                    }}
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.order')}</label>
                  <input
                    type="number"
                    required
                    value={featuredProjectForm.order}
                    onChange={(e) => setFeaturedProjectForm({ ...featuredProjectForm, order: parseInt(e.target.value) || 0 })}
                    placeholder="0"
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="featured_is_active"
                    checked={featuredProjectForm.is_active}
                    onChange={(e) => setFeaturedProjectForm({ ...featuredProjectForm, is_active: e.target.checked })}
                    className="w-4 h-4 bg-black/40 border border-white/10 rounded focus:border-red-500 focus:outline-none"
                  />
                  <label htmlFor="featured_is_active" className="text-xs text-white/60">{t('adminDashboard.active')}</label>
                </div>

                <div className="flex gap-2">
                  <Button
                    type="submit"
                    disabled={savingFeaturedProject}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white h-11 rounded-lg font-semibold"
                  >
                    {savingFeaturedProject ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {t('adminDashboard.saving')}
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        {editingFeaturedProject ? t('adminDashboard.update') : t('adminDashboard.create')}
                      </>
                    )}
                  </Button>
                  {editingFeaturedProject && (
                    <Button
                      type="button"
                      onClick={handleCancelEditFeaturedProject}
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

        {/* Featured Projects List */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md overflow-hidden">
            <CardHeader className="border-b border-white/5 p-5">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                  <Star className="w-5 h-5 text-red-500" />
                  {t('adminDashboard.allFeaturedProjects')}
                </CardTitle>
                <Badge className="bg-red-500/20 border-red-500/30 text-red-400">
                  {featuredProjects.length}/6
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5 bg-white/5 text-white/50 text-left font-semibold">
                      <th className="p-4">{t('adminDashboard.title')}</th>
                      <th className="p-4">{t('adminDashboard.category')}</th>
                      <th className="p-4">{t('adminDashboard.order')}</th>
                      <th className="p-4">{t('adminDashboard.status')}</th>
                      <th className="p-4 text-right">{t('adminDashboard.actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {featuredProjects.map((project) => (
                      <tr key={project.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4">
                          <div className="font-bold text-white">{project.title}</div>
                          <div className="text-xs text-white/40 mt-1 truncate max-w-[200px]">{project.description}</div>
                        </td>
                        <td className="p-4 text-white/60">{project.category}</td>
                        <td className="p-4 text-white/60">{project.order}</td>
                        <td className="p-4">
                          <Badge className={project.is_active ? 'bg-green-500/20 border-green-500/30 text-green-400' : 'bg-red-500/20 border-red-500/30 text-red-400'}>
                            {project.is_active ? t('adminDashboard.active') : t('adminDashboard.inactive')}
                          </Badge>
                        </td>
                        <td className="p-4 text-right flex items-center justify-end gap-2">
                          <Button
                            onClick={() => handleEditFeaturedProject(project)}
                            variant="outline"
                            size="sm"
                            className="h-8 border-red-500/35 hover:bg-red-500/10 text-red-400 font-semibold"
                          >
                            <Edit className="w-3.5 h-3.5 mr-1" />
                            {t('adminDashboard.edit')}
                          </Button>
                          <Button
                            onClick={() => handleDeleteFeaturedProject(project.id)}
                            variant="ghost"
                            size="sm"
                            className="h-8 text-white/40 hover:text-red-500 hover:bg-red-500/10"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {featuredProjects.length === 0 && (
                      <tr>
                        <td colSpan={5} className="p-12 text-center text-white/40">
                          {t('adminDashboard.noFeaturedProjects', "No featured projects created yet")}
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
