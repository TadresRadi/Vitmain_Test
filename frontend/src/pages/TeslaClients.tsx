import { motion } from "framer-motion"
import { useTranslation } from "react-i18next"
import Navbar from "@/components/Navbar"
import Footer from "@/components/Footer"
import AnimatedBackground from "@/components/AnimatedBackground"
import { useTeslaClientImages } from "@/hooks/queries/usePortfolio"

export default function TeslaClients() {
  const { t } = useTranslation()
  const { data: teslaClientImages = [], isLoading } = useTeslaClientImages()

  return (
    <div className="min-h-screen relative text-white bg-black/40 dark:bg-black/60 transition-colors duration-1000">
      <AnimatedBackground />
      <Navbar />
      
      <main className="relative z-10 pt-24 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h1 className="text-5xl md:text-7xl font-cinematic font-bold mb-4 text-white transition-colors">
              {t("landing.teslaClientTitle", "TESLA CLIENT")}
            </h1>
            <p className="text-xl text-white/60 transition-colors">
              {t("landing.teslaClientSubtitle", "Trusted by industry leaders")}
            </p>
          </motion.div>

          {/* Grid Layout */}
          {isLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="aspect-square bg-white/10 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : teslaClientImages.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-white/60 text-lg">No Tesla clients available at this time.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {teslaClientImages.map((item: any, i: number) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: i * 0.05 }}
                  className="relative group cursor-pointer overflow-hidden rounded-lg"
                >
                  <img
                    src={item.image_url}
                    alt={item.title || t("landing.teslaClientTitle", "TESLA CLIENT")}
                    className="w-full aspect-square object-cover transition-transform duration-700 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent opacity-70 group-hover:opacity-90 transition-opacity duration-500" />
                  {item.title && (
                    <div className="absolute bottom-0 left-0 right-0 p-4 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
                      <h3 className="text-sm font-bold text-white line-clamp-2">{item.title}</h3>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </main>
      
      <Footer />
    </div>
  )
}