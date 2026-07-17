import { useState, useEffect } from 'react'

interface MousePosition {
  x: number
  y: number
  px: number
  py: number
}

export function useMouseFollower(isHovering: boolean) {
  const [mousePosition, setMousePosition] = useState<MousePosition>({ x: 0, y: 0, px: 0, py: 0 })
  const [smoothedMousePosition, setSmoothedMousePosition] = useState({ px: 0, py: 0 })

  useEffect(() => {
    if (!isHovering) return

    const smoothFactor = 0.15
    const animationFrame = () => {
      setSmoothedMousePosition((prev) => ({
        px: prev.px + (mousePosition.px - prev.px) * smoothFactor,
        py: prev.py + (mousePosition.py - prev.py) * smoothFactor,
      }))
    }

    const interval = setInterval(animationFrame, 16) // ~60fps
    return () => clearInterval(interval)
  }, [mousePosition, isHovering])

  const handleMouseMove = (e: React.MouseEvent<HTMLElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const px = e.clientX - rect.left
    const py = e.clientY - rect.top
    const pctX = px / rect.width
    setMousePosition({ x: pctX, y: py, px, py })
  }

  return { mousePosition, smoothedMousePosition, handleMouseMove }
}
