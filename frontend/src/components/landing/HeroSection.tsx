import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useState, useRef } from 'react'
import { useMouseFollower } from '@/hooks/useMouseFollower'

export function HeroSection() {
  const { t } = useTranslation()
  const [isHovering, setIsHovering] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  const { mousePosition, smoothedMousePosition, handleMouseMove } = useMouseFollower(isHovering)

  // Touch handlers for mobile
  const handleTouchStart = () => setIsHovering(true)
  const handleTouchEnd = () => setIsHovering(false)
  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isHovering) setIsHovering(true)
    const touch = e.touches[0]
    const target = e.currentTarget as HTMLElement
    const fakeMouseEvent = {
      clientX: touch.clientX,
      clientY: touch.clientY,
      currentTarget: target,
      target: target,
    } as any
    handleMouseMove(fakeMouseEvent)
  }

  return (
    <section className="hero-section relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
      <div className="absolute inset-0 z-0">
        <video
          ref={videoRef}
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          className="absolute inset-0 w-full h-full object-cover"
          style={{
            willChange: 'auto',
            transform: 'translateZ(0)',
            backfaceVisibility: 'hidden',
          }}
        >
          <source src="/Backeground-video.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/60" />
      </div>

      <div className="relative z-10 text-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          className="relative inline-block"
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
          onMouseMove={handleMouseMove as any}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          onTouchMove={handleTouchMove}
        >
          <motion.h1
            dir="ltr"
            className="text-[5rem] sm:text-[8rem] md:text-[12rem] lg:text-[14rem] font-bold text-white leading-none select-none cursor-pointer relative flex justify-center transition-colors duration-1000"
            style={{ fontFamily: 'Helvetica, Arial, sans-serif' }}
            whileHover={{ scale: 1.02 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            {'VITAMIN'.split('').map((letter, index) => (
              <motion.span
                key={index}
                className="inline-block"
                initial={{ filter: 'blur(0px)' }}
                animate={{
                  filter: isHovering
                    ? `blur(${Math.max(0, 18 - Math.abs(mousePosition.x - (index + 0.5) / 7) * 100)}px)`
                    : 'blur(0px)',
                }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
              >
                {letter}
              </motion.span>
            ))}
          </motion.h1>

          {isHovering && (
            <motion.div
              className="absolute pointer-events-none"
              style={{
                left: smoothedMousePosition.px || 0,
                top: smoothedMousePosition.py || 0,
                transform: 'translate(-50%, -50%)',
              }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            >
              <div className="relative">
                <motion.div
                  className="w-32 h-32 bg-vitamin-base/20 rounded-full blur-2xl"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                />
                <motion.div
                  className="absolute top-2 left-2 w-20 h-20 bg-vitamin-600/30 rounded-full blur-xl"
                  animate={{ scale: [1, 0.8, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
                />
              </div>
            </motion.div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="mt-8"
        >
          <p className="text-lg md:text-2xl text-white/80 font-light max-w-2xl mx-auto mb-10 transition-colors duration-1000">
            {t('landing.heroDesc')}
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Button
              size="lg"
              className="bg-vitamin-base hover:bg-vitamin-700 text-white px-10 py-6 text-lg glass-effect hover:scale-105 transition-all duration-300"
              asChild
            >
              <Link to="/pricing">
                {t('landing.startCreating')} <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white/20 text-white bg-black/20 dark:bg-black/40 hover:bg-white/10 px-10 py-6 text-lg hover:scale-105 transition-all duration-300"
              asChild
            >
              <Link to="/pricing">{t('landing.viewPricing')}</Link>
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}