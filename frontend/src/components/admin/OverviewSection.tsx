import { useTranslation } from "react-i18next"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, MessageSquare, Image as ImageIcon, BarChart3, DollarSign } from "lucide-react"
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6']

interface OverviewSectionProps {
  data: any
}

function StatCard({ title, value, icon: Icon, color }: { title: string; value: number; icon: any; color: string }) {
  return (
    <Card className="bg-black/45 border-red-500/20 backdrop-blur-md relative overflow-hidden group hover:border-red-500/40 transition-colors">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/40 text-xs font-bold uppercase tracking-wider">{title}</p>
            <p className="text-3xl font-extrabold text-white mt-2 font-sans tracking-tight">{value}</p>
          </div>
          <div className={`p-3 rounded-xl bg-white/5 group-hover:scale-105 transition-transform duration-300`}>
            <Icon className={`w-6 h-6 ${color}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function OverviewSection({ data }: OverviewSectionProps) {
  const { t } = useTranslation()
  if (!data) return <div className="text-white/40 text-xs py-10">Accessing platform statistics...</div>

  return (
    <div className="space-y-8">
      <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
        <BarChart3 className="w-8 h-8 text-red-500" />
        {t('adminDashboard.overview', "Real-Time Platform Performance")}
      </h2>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title={t('adminDashboard.totalUsers', "Total Explorers & Clients")} value={data.total_users} icon={Users} color="text-red-500" />
        <StatCard title={t('adminDashboard.totalPaymentsReceived', "Total Payments Received")} value={data.total_payments || 0} icon={DollarSign} color="text-green-400" />
        <StatCard title={t('adminDashboard.postsGenerated', "Premium Posts Generated")} value={data.total_posts} icon={MessageSquare} color="text-yellow-500" />
        <StatCard title={t('adminDashboard.imagesGenerated', "Campaign Visual Mocks")} value={data.total_images} icon={ImageIcon} color="text-blue-500" />
      </div>

      {/* Data Visualization Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <Card className="bg-black/45 border-red-500/20 backdrop-blur-md overflow-hidden">
          <CardHeader className="border-b border-white/5 bg-white/5 p-4">
            <CardTitle className="text-sm font-bold text-white uppercase tracking-wider">{t('adminDashboard.userGrowth', "User Enrollment Timeline")}</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.user_growth}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="date" stroke="#666" style={{ fontSize: '10px' }} />
                <YAxis stroke="#666" style={{ fontSize: '10px' }} />
                <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #ef4444', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="count" stroke="#ef4444" strokeWidth={2.5} dot={{ fill: '#ef4444', r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-black/45 border-red-500/20 backdrop-blur-md overflow-hidden">
          <CardHeader className="border-b border-white/5 bg-white/5 p-4">
            <CardTitle className="text-sm font-bold text-white uppercase tracking-wider">{t('adminDashboard.subscriptionDistribution', "SaaS Subscription Distribution")}</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data.subscription_distribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry: any) => `${entry.plan}: ${entry.count}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {data.subscription_distribution.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #ef4444', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

      </div>
    </div>
  )
}
