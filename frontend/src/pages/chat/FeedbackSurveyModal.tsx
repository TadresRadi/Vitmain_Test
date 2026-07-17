import type { Dispatch, SetStateAction } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Star, X } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import type { FeedbackPayload } from '@/types/api'

interface FeedbackSurveyModalProps {
  open: boolean
  submitted: boolean
  feedbackData: FeedbackPayload
  setFeedbackData: Dispatch<SetStateAction<FeedbackPayload>>
  onClose: () => void
  onSubmit: () => void
}

const ratings = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

export function FeedbackSurveyModal({
  open,
  submitted,
  feedbackData,
  setFeedbackData,
  onClose,
  onSubmit,
}: FeedbackSurveyModalProps) {
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
            className="glass-dark border border-white/20 rounded-2xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Star className="h-5 w-5 text-vitamin-base" />
                {t('chat.feedbackSurvey', 'Feedback Survey')}
              </h3>
              <button
                onClick={onClose}
                className="text-white/60 hover:text-white transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {submitted ? (
              <SubmittedFeedback />
            ) : (
              <div className="space-y-6">
                <p className="text-sm text-white/60">
                  {t(
                    'chat.feedbackSurveyDesc',
                    'Help us improve our service by sharing your experience.'
                  )}
                </p>

                <RatingField
                  label={t(
                    'chat.overallSatisfaction',
                    'Rate your overall satisfaction with the service from 1 to 10.'
                  )}
                  value={feedbackData.overallSatisfaction}
                  onChange={(rating) =>
                    setFeedbackData((prev) => ({ ...prev, overallSatisfaction: rating }))
                  }
                />

                <RatingField
                  label={t(
                    'chat.postsSatisfaction',
                    'Rate your satisfaction with the generated posts from 1 to 10.'
                  )}
                  value={feedbackData.postsSatisfaction}
                  onChange={(rating) =>
                    setFeedbackData((prev) => ({ ...prev, postsSatisfaction: rating }))
                  }
                />

                <RatingField
                  label={t(
                    'chat.imagesSatisfaction',
                    'Rate your satisfaction with the generated images and image quality from 1 to 10.'
                  )}
                  value={feedbackData.imagesSatisfaction}
                  onChange={(rating) =>
                    setFeedbackData((prev) => ({ ...prev, imagesSatisfaction: rating }))
                  }
                />

                <div>
                  <label className="block text-sm font-medium text-white mb-3">
                    {t(
                      'chat.suggestions',
                      'Do you have any suggestions, improvements, or features you would like to see added to the website?'
                    )}
                  </label>
                  <textarea
                    value={feedbackData.suggestions}
                    onChange={(e) =>
                      setFeedbackData((prev) => ({ ...prev, suggestions: e.target.value }))
                    }
                    rows={4}
                    className="w-full bg-white/10 border border-white/20 text-white placeholder-white/40 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-vitamin-base resize-none"
                    placeholder={t('chat.suggestionsPlaceholder', 'Share your thoughts...')}
                  />
                </div>

                <Button
                  onClick={onSubmit}
                  disabled={
                    feedbackData.overallSatisfaction === 0 ||
                    feedbackData.postsSatisfaction === 0 ||
                    feedbackData.imagesSatisfaction === 0
                  }
                  className="w-full bg-vitamin-base hover:bg-vitamin-700 text-white font-medium h-11 rounded-xl"
                >
                  {t('chat.submitFeedback', 'Submit Feedback')}
                </Button>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

function SubmittedFeedback() {
  const { t } = useTranslation()

  return (
    <div className="text-center py-8">
      <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
        <Star className="h-8 w-8 text-green-400" />
      </div>
      <h4 className="text-lg font-bold text-white mb-2">
        {t('chat.feedbackSubmitted', 'Thank you for your feedback!')}
      </h4>
      <p className="text-sm text-white/60">
        {t(
          'chat.feedbackSubmittedDesc',
          'Your responses have been recorded. We appreciate your input.'
        )}
      </p>
    </div>
  )
}

function RatingField({
  label,
  value,
  onChange,
}: {
  label: string
  value: number
  onChange: (rating: number) => void
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-white mb-3">{label}</label>
      <div className="flex gap-2">
        {ratings.map((rating) => (
          <button
            key={rating}
            onClick={() => onChange(rating)}
            className={`w-8 h-8 rounded-lg text-sm font-medium transition-all ${
              value === rating
                ? 'bg-vitamin-base text-white'
                : 'bg-white/10 text-white/60 hover:bg-white/20'
            }`}
          >
            {rating}
          </button>
        ))}
      </div>
    </div>
  )
}
