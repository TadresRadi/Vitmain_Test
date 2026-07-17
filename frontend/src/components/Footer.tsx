import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function Footer() {
  const { t } = useTranslation()

  return (
    <footer className="border-t border-white/10 py-12 px-4 bg-black/40 dark:bg-black/60 transition-colors duration-1000 mt-auto relative z-10">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="text-2xl font-cinematic font-bold text-white transition-colors">
          Vitamin
        </div>
        <div className="flex gap-8 text-sm text-white/60 transition-colors">
          <Link to="/about" className="hover:text-vitamin-base transition-colors">
            {t('footer.aboutUs')}
          </Link>
          <Link to="/work" className="hover:text-vitamin-base transition-colors">
            {t('footer.ourWork')}
          </Link>
          <Link to="/pricing" className="hover:text-vitamin-base transition-colors">
            {t('footer.pricing')}
          </Link>
          <Link to="/contact" className="hover:text-vitamin-base transition-colors">
            {t('footer.contact')}
          </Link>
        </div>
        <div className="text-white/40 text-sm transition-colors">
          {t('landing.footer.copyright')}
        </div>
      </div>
    </footer>
  )
}
