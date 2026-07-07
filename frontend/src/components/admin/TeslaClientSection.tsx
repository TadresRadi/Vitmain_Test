import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Plus, Edit, Trash2, Save, Loader2, Car } from "lucide-react"
import { adminApi } from "@/lib/axios"

interface TeslaClientImage {
  id: number
  title: string
  image_url?: string
  order: number
  is_active: boolean
}

export default function TeslaClientSection() {
  const { t } = useTranslation()
  const [images, setImages] = useState<TeslaClientImage[]>([])
  const [editingImage, setEditingImage] = useState<TeslaClientImage | null>(null)
  const [imageForm, setImageForm] = useState({
    title: '',
    image: null as File | null,
    order: 0,
    is_active: true
  })
  const [savingImage, setSavingImage] = useState(false)

  const fetchImages = async () => {
    try {
      const res = await adminApi.get("/portfolio/tesla-client-images/all/")
      setImages(res.data)
    } catch (err: any) {
      console.error('Failed to fetch Tesla Client images:', err)
    }
  }

  useEffect(() => {
    fetchImages()
  }, [])

  const handleSaveImage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingImage && !imageForm.image) {
      alert(t('adminDashboard.teslaClientImageRequired', 'Please select an image to upload.'))
      return
    }

    setSavingImage(true)
    try {
      const formData = new FormData()
      formData.append('title', imageForm.title)
      formData.append('order', imageForm.order.toString())
      formData.append('is_active', imageForm.is_active.toString())
      if (imageForm.image) {
        formData.append('image', imageForm.image)
      }

      if (editingImage) {
await adminApi.put(`/portfolio/tesla-client-images/${editingImage.id}/`, formData)
        alert(t('adminDashboard.teslaClientUpdatedSuccess', 'Tesla Client image updated successfully.'))
      } else {
await adminApi.post('/portfolio/tesla-client-images/', formData)
        alert(t('adminDashboard.teslaClientCreatedSuccess', 'Tesla Client image added successfully.'))
      }
      setEditingImage(null)
      setImageForm({
        title: '',
        image: null,
        order: 0,
        is_active: true
      })
      fetchImages()
    } catch (err: any) {
      console.error("Failed to save Tesla Client image", err)
      alert(err.response?.data?.detail || err.response?.data?.image?.[0] || t('adminDashboard.failedSaveTeslaClient', 'Failed to save Tesla Client image.'))
    } finally {
      setSavingImage(false)
    }
  }

  const handleEditImage = (item: TeslaClientImage) => {
    setEditingImage(item)
    setImageForm({
      title: item.title,
      image: null,
      order: item.order,
      is_active: item.is_active
    })
  }

  const handleDeleteImage = async (imageId: number) => {
    if (!confirm(t('adminDashboard.confirmDeleteTeslaClient', 'Delete this Tesla Client image?'))) return
    try {
      await adminApi.delete(`/portfolio/tesla-client-images/${imageId}/`)
      alert(t('adminDashboard.teslaClientDeletedSuccess', 'Tesla Client image deleted successfully.'))
      fetchImages()
    } catch (err: any) {
      console.error("Failed to delete Tesla Client image", err)
      alert(err.response?.data?.error || err.response?.data?.detail || t('adminDashboard.failedDeleteTeslaClient', 'Failed to delete Tesla Client image.'))
    }
  }

  const handleCancelEdit = () => {
    setEditingImage(null)
    setImageForm({
      title: '',
      image: null,
      order: 0,
      is_active: true
    })
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md sticky top-[170px]">
            <CardHeader className="border-b border-white/5 pb-4">
              <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                <Plus className="w-5 h-5 text-red-500" />
                {editingImage ? t('adminDashboard.editTeslaClientImage', 'Edit Image') : t('adminDashboard.addTeslaClientImage', 'Add Image')}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleSaveImage} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.title')}</label>
                  <input
                    type="text"
                    value={imageForm.title}
                    onChange={(e) => setImageForm({ ...imageForm, title: e.target.value })}
                    placeholder={t('adminDashboard.teslaClientTitlePlaceholder', 'Optional label / alt text')}
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.image')}</label>
                  <input
                    type="file"
                    accept="image/*"
                    required={!editingImage}
                    onChange={(e) => {
                      const file = e.target.files?.[0] || null
                      if (file && file.name.length > 100) {
                        alert('Filename is too long (max 100 characters). Please rename the file.')
                        e.target.value = ''
                        return
                      }
                      setImageForm({ ...imageForm, image: file })
                    }}
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.order')}</label>
                  <input
                    type="number"
                    required
                    value={imageForm.order}
                    onChange={(e) => setImageForm({ ...imageForm, order: parseInt(e.target.value) || 0 })}
                    placeholder="0"
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="tesla_is_active"
                    checked={imageForm.is_active}
                    onChange={(e) => setImageForm({ ...imageForm, is_active: e.target.checked })}
                    className="w-4 h-4 bg-black/40 border border-white/10 rounded focus:border-red-500 focus:outline-none"
                  />
                  <label htmlFor="tesla_is_active" className="text-xs text-white/60">{t('adminDashboard.active')}</label>
                </div>

                <div className="flex gap-2">
                  <Button
                    type="submit"
                    disabled={savingImage}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white h-11 rounded-lg font-semibold"
                  >
                    {savingImage ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {t('adminDashboard.saving')}
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        {editingImage ? t('adminDashboard.update') : t('adminDashboard.create')}
                      </>
                    )}
                  </Button>
                  {editingImage && (
                    <Button
                      type="button"
                      onClick={handleCancelEdit}
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

        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md overflow-hidden">
            <CardHeader className="border-b border-white/5 p-5">
              <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                <Car className="w-5 h-5 text-red-500" />
                {t('adminDashboard.allTeslaClientImages', 'Tesla Client Gallery')}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5 bg-white/5 text-white/50 text-left font-semibold">
                      <th className="p-4">{t('adminDashboard.preview', 'Preview')}</th>
                      <th className="p-4">{t('adminDashboard.title')}</th>
                      <th className="p-4">{t('adminDashboard.order')}</th>
                      <th className="p-4">{t('adminDashboard.status')}</th>
                      <th className="p-4 text-right">{t('adminDashboard.actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {images.map((item) => (
                      <tr key={item.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4">
                          {item.image_url ? (
                            <img
                              src={item.image_url}
                              alt={item.title || 'Tesla Client'}
                              className="w-16 h-16 object-cover rounded-lg border border-white/10"
                            />
                          ) : (
                            <div className="w-16 h-16 rounded-lg bg-white/5 border border-white/10" />
                          )}
                        </td>
                        <td className="p-4 text-white">{item.title || '—'}</td>
                        <td className="p-4 text-white/60">{item.order}</td>
                        <td className="p-4">
                          <Badge className={item.is_active ? 'bg-green-500/20 border-green-500/30 text-green-400' : 'bg-red-500/20 border-red-500/30 text-red-400'}>
                            {item.is_active ? t('adminDashboard.active') : t('adminDashboard.inactive')}
                          </Badge>
                        </td>
                        <td className="p-4 text-right flex items-center justify-end gap-2">
                          <Button
                            onClick={() => handleEditImage(item)}
                            variant="outline"
                            size="sm"
                            className="h-8 border-red-500/35 hover:bg-red-500/10 text-red-400 font-semibold"
                          >
                            <Edit className="w-3.5 h-3.5 mr-1" />
                            {t('adminDashboard.edit')}
                          </Button>
                          <Button
                            onClick={() => handleDeleteImage(item.id)}
                            variant="ghost"
                            size="sm"
                            className="h-8 text-white/40 hover:text-red-500 hover:bg-red-500/10"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {images.length === 0 && (
                      <tr>
                        <td colSpan={5} className="p-8 text-center text-white/40">
                          {t('adminDashboard.noTeslaClientImages', 'No Tesla Client images yet. Add images to display them on the homepage.')}
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
