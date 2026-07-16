import { motion, AnimatePresence } from "framer-motion"
import { X } from "lucide-react"
import type { ReactNode } from "react"

interface ModalProps {
  open: boolean
  onClose: () => void
  title?: ReactNode
  icon?: ReactNode
  children: ReactNode
  maxWidth?: string  // defaults to "max-w-md"
}

export function Modal({ open, onClose, title, icon, children, maxWidth = "max-w-md" }: ModalProps) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className={`glass-dark border border-white/20 rounded-2xl p-6 ${maxWidth} w-full max-h-[90vh] overflow-y-auto`}
            onClick={(e) => e.stopPropagation()}
          >
            {title && (
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  {icon}
                  {title}
                </h3>
                <button onClick={onClose} className="text-white/60 hover:text-white transition-colors">
                  <X className="h-5 w-5" />
                </button>
              </div>
            )}
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}