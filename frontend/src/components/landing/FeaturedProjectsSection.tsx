import { useTranslation } from "react-i18next"
import { motion } from "framer-motion"
import { useFeaturedProjects } from "@/hooks/queries/usePortfolio"


export function FeaturedProjectsSection() {
  const { t } = useTranslation()
  const { data: featuredProjects = [] } = useFeaturedProjects()

  return (
    <section className="relative py-32 px-4 border-t border-white/5 bg-black/20 dark:bg-black/40 backdrop-blur-sm transition-colors duration-1000">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl font-cinematic font-bold mb-4 text-white transition-colors">{t("landing.featuredProjectsTitle", "We Highly Recommend These Clients")}</h2>
          <p className="text-xl text-white/60 transition-colors">{t("landing.featuredProjectsSubtitle", "Our latest and greatest work")}</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredProjects.map((project: any, i: number) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              className="relative group cursor-pointer overflow-hidden rounded-2xl"
            >
              <div className="aspect-[4/5] overflow-hidden">
                <img
                  src={project.image_url}
                  alt={project.title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 opacity-70 group-hover:opacity-100"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-80" />
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-8 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                <span className="text-vitamin-base font-medium tracking-wider uppercase text-sm mb-2 block">{project.category}</span>
                <h3 className="text-3xl font-bold text-white">{project.title}</h3>
                <p className="text-white/60 text-sm mt-2 line-clamp-2">{project.description}</p>
              </div>
            </motion.div>
          ))}

          {featuredProjects.length === 0 && (
            <div className="col-span-full text-center py-12 text-white/40">
              {t("landing.noFeaturedProjects", "No featured projects yet. Check back soon.")}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
