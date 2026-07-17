import { AnimatePresence, motion } from 'framer-motion'
import type { ReactNode } from 'react'
import { FileText, RefreshCw, X } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'

interface NewPostsOptionsModalProps {
  open: boolean
  onClose: () => void
  onUseNewBusinessInfo: () => void
  onUseExistingBusinessInfo: () => void
}

export function NewPostsOptionsModal({
  open,
  onClose,
  onUseNewBusinessInfo,
  onUseExistingBusinessInfo,
}: NewPostsOptionsModalProps) {
  const { t } = useTranslation()

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="glass-dark border border-white/20 rounded-2xl p-6 max-w-md w-full"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <RefreshCw className="h-5 w-5 text-vitamin-base" />
                {t('chat.generateNewPosts', 'Generate New Posts and Images')}
              </h3>
              <button
                onClick={onClose}
                className="text-white/60 hover:text-white transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <p className="text-sm text-white/60 mb-6">
              {t(
                'chat.generateNewPostsDesc',
                'Create a fresh set of marketing content for your business.'
              )}
            </p>

            <div className="space-y-4">
              <OptionCard
                icon={<FileText className="h-5 w-5" />}
                title={t('chat.useNewBusinessInfo', 'Use New Business Information')}
                description={t(
                  'chat.useNewBusinessInfoDesc',
                  'Provide new business details to generate completely different content.'
                )}
                onClick={onUseNewBusinessInfo}
              />

              <OptionCard
                icon={<RefreshCw className="h-5 w-5" />}
                title={t('chat.useExistingBusinessInfo', 'Use Existing Business Information')}
                description={t(
                  'chat.useExistingBusinessInfoDesc',
                  'Regenerate content using your current business profile.'
                )}
                onClick={onUseExistingBusinessInfo}
              />
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

function OptionCard({
  icon,
  title,
  description,
  onClick,
}: {
  icon: ReactNode
  title: string
  description: string
  onClick: () => void
}) {
  return (
    <Card
      className="glass-dark border border-white/20 p-4 hover:border-vitamin-base/50 transition-colors cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-vitamin-base/15 text-vitamin-base shrink-0">{icon}</div>
        <div>
          <h4 className="text-sm font-bold text-white mb-1">{title}</h4>
          <p className="text-xs text-white/60">{description}</p>
        </div>
      </div>
    </Card>
  )
}
