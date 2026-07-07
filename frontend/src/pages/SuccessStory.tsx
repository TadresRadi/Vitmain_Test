import { motion } from "framer-motion"
import { useTranslation } from "react-i18next"
import Navbar from "@/components/Navbar"
import Footer from "@/components/Footer"
import AnimatedBackground from "@/components/AnimatedBackground"

export default function SuccessStory() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen relative text-white bg-black/40 dark:bg-black/60 transition-colors duration-1000">
      <AnimatedBackground />
      <Navbar />

      <main className="relative z-10 pt-24 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-4 text-white">
              {t("landing.successStoryTitle", "Success Story")}
            </h1>
            <p className="text-xl text-white/60">
              {t("landing.successStorySubtitle", "How we helped customers win")}
            </p>
          </motion.div>

          <section className="space-y-8">
            <div className="prose prose-invert max-w-4xl mx-auto text-left">
              <h2>{t("landing.successStoryHeading", "Featured Success")}</h2>
              <p>
                {t(
                  "landing.successStoryBody",
                  "We partnered with brand X to deliver measurable results. This page is a placeholder — replace with real success stories content."
                )}
              </p>
            </div>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  )
}