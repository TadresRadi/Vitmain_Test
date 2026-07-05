import { Link } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { motion } from "framer-motion"
import { useEffect, useState, useRef } from "react"
import { useTeslaClientImages } from "@/hooks/queries/usePortfolio"

const fallbackTeslaClientImages = [
  {
    id: "fallback-tesla-1",
    title: "Signature Activation",
    image_url: "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&q=80&w=900",
  },
  {
    id: "fallback-tesla-2",
    title: "Launch Experience",
    image_url: "https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&q=80&w=900",
  },
  {
    id: "fallback-tesla-3",
    title: "Premium Client Work",
    image_url: "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?auto=format&fit=crop&q=80&w=900",
  },
]

export function TeslaClientsSection() {
  const { t } = useTranslation()
  const { data: teslaClientImages = [] } = useTeslaClientImages()
  const visibleImages = teslaClientImages.length > 0 ? teslaClientImages : fallbackTeslaClientImages
  const [carouselPosition, setCarouselPosition] = useState(0)
  const carouselRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const scrollCarousel = () => {
      setCarouselPosition(prev => {
        const newPosition = prev - 1
        if (newPosition <= -visibleImages.length) {
          return 0
        }
        return newPosition
      })
    }

    const interval = setInterval(scrollCarousel, 3000)
    return () => clearInterval(interval)
  }, [visibleImages.length])

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

        <div className="relative overflow-hidden">
          <motion.div
            ref={carouselRef}
            animate={{ x: `${carouselPosition * 100}%` }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            className="flex gap-6"
            style={{ width: `${visibleImages.length * 100}%` }}
          >
            {visibleImages.map((item: any, i: number) => (
              <Link
                key={item.id}
                to="/tesla-clients"
                className="flex-shrink-0 w-1/2 md:w-1/3 lg:w-1/4"
              >
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.05 }}
                  className="relative group cursor-pointer overflow-hidden rounded-2xl"
                >
                  <img
                    src={item.image_url}
                    alt={item.title || t("landing.teslaClientTitle", "TESLA CLIENT")}
                    className="w-full aspect-[4/3] object-cover transition-all duration-700 group-hover:scale-110 blur-sm group-hover:blur-[2px]"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent opacity-70 group-hover:opacity-90 transition-opacity duration-500" />
                  {item.title && (
                    <div className="absolute bottom-0 left-0 right-0 p-6 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
                      <h3 className="text-xl font-bold text-white">{item.title}</h3>
                    </div>
                  )}
                </motion.div>
              </Link>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}
