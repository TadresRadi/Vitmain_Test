import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'
import { Users, Award, Target, Zap } from 'lucide-react'

const valueIcons = [
  <Zap className="w-8 h-8" />,
  <Target className="w-8 h-8" />,
  <Users className="w-8 h-8" />,
  <Award className="w-8 h-8" />,
]

export default function About() {
  const { t } = useTranslation()

  const stats = [
    { value: '750+', label: t('about.statsClients') },
    { value: '2000+', label: t('about.statsProjects') },
    { value: '7+', label: t('about.statsAwards') },
    { value: '8', label: t('about.statsYears') },
  ]

  const values = t('about.values', { returnObjects: true }) as { title: string; desc: string }[]

  return (
    <div className="relative z-10 pt-32 pb-20 px-4 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-24"
        >
          <h1 className="text-5xl md:text-7xl font-cinematic font-bold text-white mb-6">
            {t('about.title')}{' '}
            <span className="text-vitamin-base">{t('about.titleHighlight')}</span>
          </h1>
          <p className="text-xl text-white/70 max-w-3xl mx-auto">{t('about.heroDesc')}</p>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-32">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold text-vitamin-base mb-2">
                {stat.value}
              </div>
              <div className="text-white/60 font-medium tracking-wide uppercase text-sm">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Story */}
        <div className="grid md:grid-cols-2 gap-16 items-center mb-32">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-cinematic font-bold text-white mb-6">
              {t('about.storyTitle')}
            </h2>
            <p className="text-white/70 text-lg leading-relaxed mb-6">{t('about.storyP1')}</p>
            <p className="text-white/70 text-lg leading-relaxed">{t('about.storyP2')}</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative h-[500px] rounded-3xl overflow-hidden glass-dark border border-white/10"
          >
            <img
              src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&q=80&w=1200"
              alt="Team collaboration"
              className="w-full h-full object-cover opacity-80"
            />
          </motion.div>
        </div>

        {/* Values */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-cinematic font-bold text-white mb-12">
            {t('about.valuesTitle')}
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            {values.map((value, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="glass-dark border border-white/10 p-8 rounded-2xl hover:border-vitamin-base/50 transition-colors"
              >
                <div className="text-vitamin-base mb-6 flex justify-center">{valueIcons[i]}</div>
                <h3 className="text-xl font-bold text-white mb-4">{value.title}</h3>
                <p className="text-white/60">{value.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
