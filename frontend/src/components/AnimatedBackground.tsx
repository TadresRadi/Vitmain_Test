import React from 'react'

const AnimatedBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0 bg-[#1f0404] dark:bg-[#030000] transition-colors duration-1000 text-white">
      {/* Simple static gradient background */}
      <div className="absolute inset-0 opacity-30 bg-gradient-to-br from-[#5a0c0c] via-transparent to-[#5a0c0c] dark:from-[#450a0a] dark:to-[#450a0a]" />

      {/* Simple ambient light sources (static) */}
      <div className="absolute -top-[20%] -left-[10%] w-[60vw] h-[60vw] bg-vitamin-base rounded-full opacity-20 dark:opacity-30 mix-blend-screen filter blur-[100px] dark:blur-[120px]" />
      <div className="absolute top-[60%] -right-[20%] w-[70vw] h-[70vw] bg-vitamin-500 dark:bg-vitamin-600 rounded-full opacity-30 dark:opacity-40 mix-blend-screen filter blur-[120px] dark:blur-[150px]" />

      {/* Cinematic Vignette */}
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_0%,#000_100%)] opacity-70 dark:opacity-90" />
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-[#0a0202] via-transparent to-[#0a0202] dark:from-black dark:to-black opacity-60 dark:opacity-70" />
    </div>
  )
}

export default AnimatedBackground
