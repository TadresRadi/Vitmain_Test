import { motion } from "framer-motion"
import { useTranslation } from "react-i18next"
import { useTeslaClientImages } from "@/hooks/queries/usePortfolio"
import { Link } from "react-router-dom"


export default function TeslaClientsSection() {
  const { t } = useTranslation()
  const { data: teslaClientImages = [], isLoading } = useTeslaClientImages()
  const visibleImages = Array.isArray(teslaClientImages) ? teslaClientImages : []

  return (
    <section className="relative py-32 px-4 border-t border-white/5 bg-black/20 dark:bg-black/40 backdrop-blur-sm transition-colors duration-1000">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl font-cinematic font-bold mb-4 text-white transition-colors">
            {t("landing.teslaClientTitle", "TESLA CLIENT")}
          </h2>
          <p className="text-xl text-white/60 transition-colors">
            {t("landing.teslaClientSubtitle", "Trusted by industry leaders")}
          </p>
        </motion.div>

        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-44 bg-white/5 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : visibleImages.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-white/60 text-lg">No Tesla client images to display.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {visibleImages.map((item: any, i: number) => (
              <motion.div
                key={item.id}
                initial={{ opacity: .5, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.03 }}
                className="relative group cursor-pointer overflow-hidden rounded-2xl"
              >
                <Link to="/tesla-clients" className="block w-full h-44 md:h-52 lg:h-44">
                  <img
                    src={item.image_url}
                    alt={item.title || t("landing.teslaClientTitle", "TESLA CLIENT")}
                    className="w-full h-full object-cover filter blur-sm opacity-50 transition-all duration-300 ease-out group-hover:blur-0 group-hover:opacity-100 group-hover:scale-105"
                    style={{ transformOrigin: 'center' }}
                  />
                </Link>

                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent opacity-70 group-hover:opacity-90 transition-opacity duration-300" />

                {item.title && (
                  <div className="absolute bottom-0 left-0 right-0 p-6 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-300">
                    <h3 className="text-xl font-bold text-white">{item.title}</h3>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}