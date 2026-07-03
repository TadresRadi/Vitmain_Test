import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Users, UserPlus, Trash2, Loader2, FileText } from "lucide-react"
import { adminApi } from "@/lib/axios"

interface User {
  id: string
  full_name?: string
  email: string
  role: string
  user_type: string
  date_joined: string
}

interface UsersSectionProps {
  onOpenUserLogs: (user: User) => void
}

export default function UsersSection({ onOpenUserLogs }: UsersSectionProps) {
  const { t } = useTranslation()
  const [users, setUsers] = useState<User[]>([])
  const [supervisorEmail, setSupervisorEmail] = useState('')
  const [supervisorPassword, setSupervisorPassword] = useState('')
  const [creatingSupervisor, setCreatingSupervisor] = useState(false)

  const fetchUsers = async () => {
    try {
      const response = await adminApi.get('/admin/users')
      setUsers(response.data)
    } catch (err) {
      console.error("Failed to fetch users:", err)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleCreateSupervisor = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreatingSupervisor(true)
    try {
      await adminApi.post('/admin/create-supervisor', {
        email: supervisorEmail,
        password: supervisorPassword
      })
      alert(t('adminDashboard.supervisorCreatedSuccess', 'Supervisor created successfully!'))
      setSupervisorEmail('')
      setSupervisorPassword('')
      fetchUsers()
    } catch (err: any) {
      console.error("Failed to create supervisor:", err)
      alert(err.response?.data?.error || t('adminDashboard.failedCreateSupervisor', 'Failed to create supervisor'))
    } finally {
      setCreatingSupervisor(false)
    }
  }

  const handleUpdateRole = async (userId: string, newRole: string) => {
    try {
      await adminApi.put(`/admin/users/${userId}/role`, { role: newRole })
      alert(t('adminDashboard.roleUpdatedSuccess', 'Role updated successfully!'))
      fetchUsers()
    } catch (err: any) {
      console.error("Failed to update role:", err)
      const message =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        t('adminDashboard.failedUpdateRole', 'Failed to update role.')
      alert(message)
    }
  }

  const handleDeleteUser = async (userId: string) => {
    if (!confirm(t('adminDashboard.confirmDelete', "Are you sure you want to delete this user?"))) return
    try {
      await adminApi.delete(`/admin/users/${userId}`)
      alert(t('adminDashboard.userDeletedSuccess', 'User deleted successfully!'))
      fetchUsers()
    } catch (err: any) {
      console.error("Failed to delete user:", err)
      const message =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        t('adminDashboard.failedDelete', 'Failed to delete user.')
      alert(message)
    }
  }

  return (
    <div className="space-y-8">
      
      {/* Split layout: Supervisor Account Creation & User Manager */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Invite/Create Supervisor Panel */}
        <div className="lg:col-span-1">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md sticky top-[170px]">
            <CardHeader className="border-b border-white/5 pb-4">
              <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                <UserPlus className="w-5 h-5 text-red-500" />
                {t('adminDashboard.inviteSupervisor', "Add Supervisor Account")}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleCreateSupervisor} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.email', "Email Address")}</label>
                  <input
                    type="email"
                    required
                    value={supervisorEmail}
                    onChange={(e) => setSupervisorEmail(e.target.value)}
                    placeholder="e.g. supervisor@vitmain.com"
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-xs text-white/60 font-semibold uppercase tracking-wider">{t('adminDashboard.password', "Temporary Password")}</label>
                  <input
                    type="password"
                    required
                    value={supervisorPassword}
                    onChange={(e) => setSupervisorPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-black/40 border border-white/10 text-white rounded-lg px-4 py-2.5 text-sm focus:border-red-500 focus:outline-none"
                  />
                </div>

                <Button 
                  type="submit" 
                  disabled={creatingSupervisor}
                  className="w-full bg-red-600 hover:bg-red-700 text-white h-11 rounded-lg font-semibold mt-2"
                >
                  {creatingSupervisor ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      {t('adminDashboard.creating', "Creating...")}
                    </>
                  ) : (
                    t('adminDashboard.createSupervisor', "Register Supervisor")
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* User Manager Table */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-black/45 border-red-500/20 backdrop-blur-md overflow-hidden">
            <CardHeader className="border-b border-white/5 p-5">
              <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-red-500" />
                {t('adminDashboard.usersManagement', "Active User Database")}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5 bg-white/5 text-white/50 text-left font-semibold">
                      <th className="p-4">{t('adminDashboard.user', "Name")}</th>
                      <th className="p-4">{t('adminDashboard.email', "Email")}</th>
                      <th className="p-4">{t('adminDashboard.role', "Role")}</th>
                      <th className="p-4">{t('adminDashboard.created', "Registered")}</th>
                      <th className="p-4 text-right">{t('adminDashboard.actions', "Audits")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4">
                          <div className="font-bold text-white leading-none">{user.full_name || 'Anonymous User'}</div>
                          <div className="text-[10px] text-white/40 mt-1 font-mono uppercase">{user.user_type}</div>
                        </td>
                        <td className="p-4 text-white/60 font-sans">{user.email}</td>
                        <td className="p-4">
                          <select
                            value={user.role}
                            onChange={(e) => handleUpdateRole(user.id, e.target.value)}
                            className="bg-black border border-white/10 text-white text-xs rounded px-2.5 py-1.5 focus:border-red-500 focus:outline-none"
                          >
                            <option value="user">{t('adminDashboard.normalUser', "User")}</option>
                            <option value="supervisor">{t('adminDashboard.supervisor', "Supervisor")}</option>
                            <option value="super_admin">{t('adminDashboard.admin', "Super Admin")}</option>
                          </select>
                        </td>
                        <td className="p-4 text-white/40 text-xs">
                          {new Date(user.date_joined).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                        </td>
                        <td className="p-4 text-right flex items-center justify-end gap-2">
                          <Button
                            onClick={() => onOpenUserLogs(user)}
                            variant="outline"
                            size="sm"
                            className="h-8 border-red-500/35 hover:bg-red-500/10 text-red-400 font-semibold"
                          >
                            <FileText className="w-3.5 h-3.5 mr-1" />
                            {t('adminDashboard.logs', "Logs")}
                          </Button>
                          
                          <Button
                            onClick={() => handleDeleteUser(user.id)}
                            variant="ghost"
                            size="sm"
                            className="h-8 text-white/40 hover:text-red-500 hover:bg-red-500/10"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
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
