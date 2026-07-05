import { useTranslation } from "react-i18next"
import { motion } from "framer-motion"
import { useBrands } from "@/hooks/queries/usePortfolio"

const fallbackBrands = [
  { id: "fallback-brand-1", name: "VITMAIN", logo_url: null },
  { id: "fallback-brand-2", name: "NOVA", logo_url: null },
  { id: "fallback-brand-3", name: "AXIS", logo_url: null },
  { id: "fallback-brand-4", name: "ORBIT", logo_url: null },
  { id: "fallback-brand-5", name: "PULSE", logo_url: null },
  { id: "fallback-brand-6", name: "LUMEN", logo_url: null },
]

export function BrandsCarousel() {
  const { t } = useTranslation()
  const { data: brands = [] } = useBrands()
  const visibleBrands = brands.length > 0 ? brands : fallbackBrands

  return (
    <section className="py-24 border-y border-white/5 bg-white/5 transition-colors duration-1000 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <h2 className="text-4xl font-cinematic font-bold mb-4 text-white transition-colors">{t("landing.clientsTitle")}</h2>
          <p className="text-lg text-white/60 transition-colors">{t("landing.clientsSubtitle")}</p>
        </motion.div>
      </div>

      <div className="relative w-full overflow-hidden">
        <div className="pointer-events-none absolute left-0 top-0 h-full w-32 z-10 bg-gradient-to-r from-black/60 to-transparent" />
        <div className="pointer-events-none absolute right-0 top-0 h-full w-32 z-10 bg-gradient-to-l from-black/60 to-transparent" />

        <div className="flex animate-marquee w-max">
          {visibleBrands.map((brand: any) => (
            <div key={brand.id} className="flex items-center justify-center h-16 w-32 group cursor-pointer shrink-0">
              {brand.logo_url && (
                <img
                  src={brand.logo_url}
                  alt={brand.name}
                  className="max-h-12 max-w-28 object-contain opacity-40 group-hover:opacity-100 transition-opacity duration-300 filter brightness-0 invert"
                  onError={(e) => {
                    const el = e.currentTarget
                    el.style.display = 'none'
                    const fb = el.nextElementSibling as HTMLElement
                    if (fb) fb.style.display = 'block'
                  }}
                />
              )}
              <span className={`${brand.logo_url ? "hidden" : "block"} text-white/30 font-cinematic font-bold text-xl tracking-widest group-hover:text-white transition-colors duration-300`}>
                {brand.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
