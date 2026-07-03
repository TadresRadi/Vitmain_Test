import { motion, useScroll, useTransform } from "framer-motion"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { HeroSection } from "@/components/landing/HeroSection"
import { FeaturedProjectsSection } from "@/components/landing/FeaturedProjectsSection"
import { TeslaClientsSection } from "@/components/landing/TeslaClientsSection"
import { BrandsCarousel } from "@/components/landing/BrandsCarousel"

export default function Landing() {
  const { t } = useTranslation()
  const { scrollYProgress } = useScroll()
  const yParallax = useTransform(scrollYProgress, [0, 1], [0, -300])

  return (
    <div className="relative">
      <HeroSection />

      {/* Who We Are */}
      <section className="relative py-32 px-4 border-t border-white/5 bg-black/20 dark:bg-black/40 backdrop-blur-sm transition-colors duration-1000">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-5xl md:text-7xl font-bold mb-6 font-cinematic leading-tight text-white transition-colors">
              {t("landing.whoWeAreTitle")}
            </h2>
            <h3 className="text-3xl text-vitamin-base mb-8">{t("landing.whoWeAreSubtitle")}</h3>
            <p className="text-xl text-white/70 leading-relaxed mb-10 transition-colors">
              {t("landing.whoWeAreDesc")}
            </p>
            <Button variant="outline" className="border-vitamin-base text-vitamin-base hover:bg-vitamin-base hover:text-white px-8 py-6 text-lg rounded-full">
              Discover Our Agency
            </Button>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1 }}
            className="relative h-[600px] rounded-3xl overflow-hidden bg-black/40 border border-white/10 transition-colors duration-1000"
            style={{ y: yParallax }}
          >
            <img 
              src="https://images.unsplash.com/photo-1600132806370-bf17e65e942f?auto=format&fit=crop&q=80&w=1200" 
              alt="Creative Agency" 
              className="w-full h-full object-cover opacity-80"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
          </motion.div>
        </div>
      </section>

      <FeaturedProjectsSection />
      <TeslaClientsSection />
      <BrandsCarousel />

      {/* Creative Process */}
      <section className="relative py-32 px-4">
        <div className="max-w-5xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-24"
          >
            <h2 className="text-5xl font-cinematic font-bold mb-4 text-white transition-colors">{t("landing.processTitle")}</h2>
            <p className="text-xl text-white/60 transition-colors">{t("landing.processSubtitle")}</p>
          </motion.div>

          <div className="space-y-16">
            {(t("landing.processSteps", { returnObjects: true }) as any[]).map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: i % 2 === 0 ? -50 : 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6 }}
                className="flex flex-col md:flex-row items-center gap-8 md:gap-16"
              >
                <div className={`w-full md:w-1/2 flex ${i % 2 === 0 ? 'md:justify-end' : 'md:order-2 md:justify-start'}`}>
                  <div className="text-[8rem] font-bold text-white/5 leading-none select-none font-cinematic transition-colors">
                    0{i + 1}
                  </div>
                </div>
                <div className={`w-full md:w-1/2 ${i % 2 === 0 ? '' : 'md:order-1 md:text-right'}`}>
                  <h3 className="text-3xl font-bold text-white mb-4 flex items-center gap-4 justify-start transition-colors">
                    {i % 2 !== 0 && <span className="hidden md:inline-block w-12 h-[2px] bg-vitamin-base" />}
                    {step.title}
                    {i % 2 === 0 && <span className="hidden md:inline-block w-12 h-[2px] bg-vitamin-base" />}
                  </h3>
                  <p className="text-lg text-white/60 leading-relaxed max-w-md transition-colors">
                    {step.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
