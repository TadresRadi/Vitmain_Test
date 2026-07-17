import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Plus, Edit, Trash2, Save, Loader2, Image as ImageIcon } from 'lucide-react'
import { api } from '@/lib/axios'

interface Brand {
  id: number
  name: string
  logo_url?: string
  order: number
  is_active: boolean
}

export default function BrandsSection() {
  const { t } = useTranslation()
  const [brands, setBrands] = useState<Brand[]>([])
  const [editingBrand, setEditingBrand] = useState<Brand | null>(null)
  const [brandForm, setBrandForm] = useState({
    name: '',
    logo: null as File | null,
    order: 0,
    is_active: true,
  })
  const [savingBrand, setSavingBrand] = useState(false)

  const fetchBrands = async () => {
    try {
      const res = await api.get('/portfolio/brands/all/')
      setBrands(res.data)
    } catch (err: any) {
      console.error('Failed to fetch brands:', err)
    }
  }

  useEffect(() => {
    fetchBrands()
  }, [])

  const handleSaveBrand = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingBrand(true)
    try {
      const formData = new FormData()
      formData.append('name', brandForm.name)
      formData.append('order', brandForm.order.toString())
      formData.append('is_active', brandForm.is_active.toString())
      if (brandForm.logo) {
        formData.append('logo', brandForm.logo)
      }

      if (editingBrand) {
        await api.put(`/portfolio/brands/${editingBrand.id}/`, formData, {})
        alert(t('adminDashboard.brandUpdatedSuccess', 'Brand updated successfully!'))
      } else {
        await api.post('/portfolio/brands/', formData, {})
        alert(t('adminDashboard.brandCreatedSuccess', 'Brand created successfully!'))
      }
      setEditingBrand(null)
      setBrandForm({
        name: '',
        logo: null,
        order: 0,
        is_active: true,
      })
      fetchBrands()
    } catch (err: any) {
      console.error('Failed to save brand', err)
      console.error('Error response:', err.response?.data)
      console.error('Error status:', err.response?.status)
      alert(
        err.response?.data?.detail ||
          err.response?.data?.error ||
          t('adminDashboard.failedSaveBrand', 'Failed to save brand')
      )
    } finally {
      setSavingBrand(false)
    }
  }

  const handleEditBrand = (brand: Brand) => {
    setEditingBrand(brand)
    setBrandForm({
      name: brand.name,
      logo: null,
      order: brand.order,
      is_active: brand.is_active,
    })
  }

  const handleDeleteBrand = async (brandId: number) => {
    if (
      !confirm(
        t('adminDashboard.confirmDeleteBrand', 'Are you sure you want to delete this brand?')
      )
    )
      return
    try {
      await api.delete(`/portfolio/brands/${brandId}/`)
      alert(t('adminDashboard.brandDeletedSuccess', 'Brand deleted successfully!'))
      fetchBrands()
    } catch (err: any) {
      console.error('Failed to delete brand', err)
      let errorMessage = t('adminDashboard.failedDeleteBrand', 'Failed to delete brand')
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      }
      alert(errorMessage)
    }
  }

  const handleCancelEditBrand = () => {
    setEditingBrand(null)
    setBrandForm({
      name: '',
      logo: null,
      order: 0,
      is_active: true,
    })
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Brand Form */}
        <div className="lg:col-span-1">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md sticky top-[170px]">
            <CardHeader className="border-b border-white/5 pb-4">
              <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                <Plus className="w-5 h-5 text-red-500" />
                {editingBrand
                  ? t('adminDashboard.editBrand', 'Edit Brand')
                  : t('adminDashboard.addNewBrand', 'Add New Brand')}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleSaveBrand} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">
                    {t('adminDashboard.name', 'Name')}
                  </label>
                  <input
                    type="text"
                    required
                    value={brandForm.name}
                    onChange={(e) => setBrandForm({ ...brandForm, name: e.target.value })}
                    placeholder="Brand name"
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">
                    {t('adminDashboard.logo', 'Logo')}
                  </label>
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
                      setBrandForm({ ...brandForm, logo: file })
                    }}
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">
                    {t('adminDashboard.order')}
                  </label>
                  <input
                    type="number"
                    required
                    value={brandForm.order}
                    onChange={(e) =>
                      setBrandForm({ ...brandForm, order: parseInt(e.target.value) || 0 })
                    }
                    placeholder="0"
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="brand_is_active"
                    checked={brandForm.is_active}
                    onChange={(e) => setBrandForm({ ...brandForm, is_active: e.target.checked })}
                    className="w-4 h-4 bg-black/40 border border-white/10 rounded focus:border-red-500 focus:outline-none"
                  />
                  <label htmlFor="brand_is_active" className="text-xs text-white/60">
                    {t('adminDashboard.active')}
                  </label>
                </div>

                <div className="flex gap-2">
                  <Button
                    type="submit"
                    disabled={savingBrand}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white h-11 rounded-lg font-semibold"
                  >
                    {savingBrand ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {t('adminDashboard.saving')}
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        {editingBrand ? t('adminDashboard.update') : t('adminDashboard.create')}
                      </>
                    )}
                  </Button>
                  {editingBrand && (
                    <Button
                      type="button"
                      onClick={handleCancelEditBrand}
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

        {/* Brands List */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md overflow-hidden">
            <CardHeader className="border-b border-white/5 p-5">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                  <ImageIcon className="w-5 h-5 text-red-500" />
                  {t('adminDashboard.allBrands', 'All Brands')}
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5 bg-white/5 text-white/50 text-left font-semibold">
                      <th className="p-4">{t('adminDashboard.name', 'Name')}</th>
                      <th className="p-4">{t('adminDashboard.logo', 'Logo')}</th>
                      <th className="p-4">{t('adminDashboard.order')}</th>
                      <th className="p-4">{t('adminDashboard.status')}</th>
                      <th className="p-4 text-right">{t('adminDashboard.actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {brands.map((brand) => (
                      <tr
                        key={brand.id}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        <td className="p-4">
                          <div className="font-bold text-white">{brand.name}</div>
                        </td>
                        <td className="p-4">
                          {brand.logo_url && (
                            <img
                              src={brand.logo_url}
                              alt={brand.name}
                              className="w-12 h-12 object-contain rounded"
                            />
                          )}
                        </td>
                        <td className="p-4 text-white/60">{brand.order}</td>
                        <td className="p-4">
                          <Badge
                            className={
                              brand.is_active
                                ? 'bg-green-500/20 border-green-500/30 text-green-400'
                                : 'bg-red-500/20 border-red-500/30 text-red-400'
                            }
                          >
                            {brand.is_active
                              ? t('adminDashboard.active')
                              : t('adminDashboard.inactive')}
                          </Badge>
                        </td>
                        <td className="p-4 text-right flex items-center justify-end gap-2">
                          <Button
                            onClick={() => handleEditBrand(brand)}
                            variant="outline"
                            size="sm"
                            className="h-8 border-red-500/35 hover:bg-red-500/10 text-red-400 font-semibold"
                          >
                            <Edit className="w-3.5 h-3.5 mr-1" />
                            {t('adminDashboard.edit')}
                          </Button>
                          <Button
                            onClick={() => handleDeleteBrand(brand.id)}
                            variant="ghost"
                            size="sm"
                            className="h-8 text-white/40 hover:text-red-500 hover:bg-red-500/10"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {brands.length === 0 && (
                      <tr>
                        <td colSpan={5} className="p-12 text-center text-white/40">
                          {t('adminDashboard.noBrands', 'No brands created yet')}
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
