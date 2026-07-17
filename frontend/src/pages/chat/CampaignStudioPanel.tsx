import { motion } from 'framer-motion'
import type { ReactNode } from 'react'
import { FileText, Image as ImageIcon, Loader2, RefreshCw, Sparkles, Star, X } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import type { AIPostGeneration, PostWithImage } from '@/types/api'

interface CampaignStudioPanelProps {
  loading: boolean
  postGen: AIPostGeneration | null
  postsWithImages: PostWithImage[] | null
  generatingPosts: boolean
  generatingImages: boolean
  showPostReview: boolean
  showPostSelection: boolean
  selectedPosts: number[]
  regeneratingPosts: boolean
  onGeneratePosts: () => void
  onGenerateImages: () => void
  onPostReviewYes: () => void
  onPostReviewNo: () => void
  onRegenerateSelectedPosts: () => void
  onTogglePostSelection: (index: number) => void
  onCancelPostSelection: () => void
  onOpenFeedbackSurvey: () => void
  onOpenNewPostsOptions: () => void
}

export function CampaignStudioPanel({
  loading,
  postGen,
  postsWithImages,
  generatingPosts,
  generatingImages,
  showPostReview,
  showPostSelection,
  selectedPosts,
  regeneratingPosts,
  onGeneratePosts,
  onGenerateImages,
  onPostReviewYes,
  onPostReviewNo,
  onRegenerateSelectedPosts,
  onTogglePostSelection,
  onCancelPostSelection,
  onOpenFeedbackSurvey,
  onOpenNewPostsOptions,
}: CampaignStudioPanelProps) {
  const { t } = useTranslation()

  return (
    <div className="flex-grow flex overflow-hidden max-w-7xl w-full mx-auto p-4">
      <div className="flex-1 flex flex-col glass-dark border border-white/10 rounded-2xl overflow-hidden bg-black/25 backdrop-blur-md">
        <div className="p-4 border-b border-white/10 bg-white/5 flex items-center justify-between">
          <div>
            <h2 className="font-bold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-vitamin-base" />
              {t('chat.campaignStudio', 'Campaign Studio')}
            </h2>
            <p className="text-xs text-white/50">
              {t('chat.studioDesc', 'Review and attach visual media assets')}
            </p>
          </div>
        </div>

        <div className="flex-grow overflow-y-auto p-4 space-y-4">
          {loading ? (
            <LoadingState />
          ) : postGen === null ? (
            <EmptyCampaignState
              generatingPosts={generatingPosts}
              onGeneratePosts={onGeneratePosts}
            />
          ) : (
            <>
              <PostList postGen={postGen} postsWithImages={postsWithImages} />

              {showPostReview && !showPostSelection && (
                <PostReviewPrompt
                  onPostReviewYes={onPostReviewYes}
                  onPostReviewNo={onPostReviewNo}
                />
              )}

              {postGen.posts_review_complete &&
                !postGen.has_images &&
                postGen.images_status !== 'processing' && (
                  <GenerateImagesPrompt
                    generatingImages={generatingImages}
                    onGenerateImages={onGenerateImages}
                  />
                )}

              {postGen.images_status === 'processing' && <ImageGenerationStatusPanel />}

              {showPostSelection && (
                <PostSelectionPanel
                  selectedPosts={selectedPosts}
                  regeneratingPosts={regeneratingPosts}
                  onTogglePostSelection={onTogglePostSelection}
                  onRegenerateSelectedPosts={onRegenerateSelectedPosts}
                  onCancelPostSelection={onCancelPostSelection}
                />
              )}
            </>
          )}
        </div>

        {postGen && (
          <BottomActions
            hasImages={postGen.has_images}
            onOpenFeedbackSurvey={onOpenFeedbackSurvey}
            onOpenNewPostsOptions={onOpenNewPostsOptions}
          />
        )}
      </div>
    </div>
  )
}

function LoadingState() {
  const { t } = useTranslation()

  return (
    <div className="h-full flex flex-col items-center justify-center text-white/40 gap-2">
      <Loader2 className="h-6 w-6 animate-spin text-vitamin-base" />
      <p className="text-xs">{t('chat.connectingStudio', 'Syncing Campaign Studio...')}</p>
    </div>
  )
}

function EmptyCampaignState({
  generatingPosts,
  onGeneratePosts,
}: {
  generatingPosts: boolean
  onGeneratePosts: () => void
}) {
  const { t } = useTranslation()

  return (
    <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-6">
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-vitamin-base to-pink-500 flex items-center justify-center shadow-lg shadow-vitamin-base/25">
        <Sparkles className="h-8 w-8 text-white animate-pulse" />
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-bold text-white">
          {t('chat.formulatePrompt', 'Formulate Premium Campaigns')}
        </h3>
        <p className="text-xs text-white/60 leading-relaxed max-w-sm">
          {t(
            'chat.formulatePromptDesc',
            'Leverage Gemini Pro to construct exactly 5 comprehensive marketing posts translated into your profile language.'
          )}
        </p>
      </div>
      <Button
        onClick={onGeneratePosts}
        disabled={generatingPosts}
        className="w-full bg-gradient-to-r from-vitamin-base to-pink-600 hover:from-vitamin-700 hover:to-pink-700 text-white font-medium h-12 rounded-xl flex items-center justify-center gap-2 shadow-lg"
      >
        {generatingPosts ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            {t('chat.formulating', 'Formulating Campaign...')}
          </>
        ) : (
          <>
            <Sparkles className="h-4 w-4" />
            {t('chat.generatePosts', 'Formulate 5 Campaign Posts')}
          </>
        )}
      </Button>
    </div>
  )
}

function PostList({
  postGen,
  postsWithImages,
}: {
  postGen: AIPostGeneration
  postsWithImages: PostWithImage[] | null
}) {
  const { t } = useTranslation()

  return (
    <div className="space-y-4">
      {postGen.posts.map((post, idx) => {
        const imageObj = postsWithImages?.find((p) => p.post_index === idx)

        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.05 }}
          >
            <Card className="overflow-hidden glass-dark border border-white/10 transition-all duration-200 bg-black/40">
              {imageObj?.image_url && (
                <div className="relative aspect-video w-full overflow-hidden border-b border-white/10">
                  <img
                    src={imageObj.image_url}
                    alt={`Post #${idx + 1} Visual`}
                    className="w-full h-full object-cover brightness-95 hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-2 left-2 bg-black/75 px-2 py-0.5 rounded text-[10px] text-vitamin-400 font-bold border border-vitamin-500/20 uppercase tracking-wider">
                    {t('chat.visualMock', 'Visual Asset Mock')}
                  </div>
                </div>
              )}

              <div className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-white/40 border-white/15">
                    {`Post #${idx + 1}`}
                  </Badge>
                </div>

                <p className="text-sm text-white/80 leading-relaxed font-sans select-all whitespace-pre-line">
                  {post}
                </p>
              </div>
            </Card>
          </motion.div>
        )
      })}
    </div>
  )
}

function PostReviewPrompt({
  onPostReviewYes,
  onPostReviewNo,
}: {
  onPostReviewYes: () => void
  onPostReviewNo: () => void
}) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6 p-4 rounded-xl border border-vitamin-500/25 bg-vitamin-base/5 space-y-4"
    >
      <PanelTitle
        icon={<FileText className="w-5 h-5" />}
        title={t('postReview.title', 'Review Your Posts')}
        description={t('postReview.message', 'Do you want to modify any of these posts?')}
      />

      <div className="flex gap-3">
        <Button
          onClick={onPostReviewYes}
          className="flex-1 bg-vitamin-base hover:bg-vitamin-700 text-white font-medium h-10 rounded-lg"
        >
          {t('postReview.yes', 'Yes')}
        </Button>
        <Button
          onClick={onPostReviewNo}
          variant="outline"
          className="flex-1 border-white/20 text-black dark:text-white hover:bg-vitamin-base/10 dark:hover:bg-white/10 hover:text-black dark:hover:text-white h-10 rounded-lg"
        >
          {t('postReview.no', 'No')}
        </Button>
      </div>
    </motion.div>
  )
}

function GenerateImagesPrompt({
  generatingImages,
  onGenerateImages,
}: {
  generatingImages: boolean
  onGenerateImages: () => void
}) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6 p-4 rounded-xl border border-vitamin-500/25 bg-vitamin-base/5 space-y-4"
    >
      <PanelTitle
        icon={<ImageIcon className="w-5 h-5" />}
        title={t('postReview.generateImagesTitle', 'Generate Images')}
        description={t(
          'postReview.generateImagesDesc',
          'Your posts are ready. Generate matching visuals for all 5 campaign posts.'
        )}
      />

      <Button
        onClick={onGenerateImages}
        disabled={generatingImages}
        className="w-full bg-gradient-to-r from-vitamin-base to-pink-500 hover:from-vitamin-700 hover:to-pink-600 text-white font-semibold text-xs h-10 rounded-lg flex items-center justify-center gap-2 shadow-md"
      >
        {generatingImages ? (
          <>
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            {t('chat.attachingVisuals', 'Attaching Visuals...')}
          </>
        ) : (
          <>
            <Sparkles className="h-3.5 w-3.5 text-white" />
            {t('postReview.generateImages', 'Generate Images')}
          </>
        )}
      </Button>
    </motion.div>
  )
}

function ImageGenerationStatusPanel() {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6 p-4 rounded-xl border border-vitamin-500/25 bg-vitamin-base/5 space-y-4"
    >
      <PanelTitle
        icon={<Loader2 className="w-5 h-5 animate-spin" />}
        title={t('chat.generatingImages', 'Generating Images')}
        description={t(
          'chat.generatingImagesDesc',
          'Your visual assets are being generated. This may take a moment.'
        )}
      />
    </motion.div>
  )
}

function PostSelectionPanel({
  selectedPosts,
  regeneratingPosts,
  onTogglePostSelection,
  onRegenerateSelectedPosts,
  onCancelPostSelection,
}: {
  selectedPosts: number[]
  regeneratingPosts: boolean
  onTogglePostSelection: (index: number) => void
  onRegenerateSelectedPosts: () => void
  onCancelPostSelection: () => void
}) {
  const { t } = useTranslation()

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6 p-4 rounded-xl border border-vitamin-500/25 bg-vitamin-base/5 space-y-4"
    >
      <PanelTitle
        icon={<FileText className="w-5 h-5" />}
        title={t('postReview.title', 'Review Your Posts')}
        description={t(
          'postReview.selectPosts',
          'Select the post numbers you would like to modify.'
        )}
      />

      <div className="grid grid-cols-5 gap-2">
        {Array.from({ length: 5 }, (_, i) => (
          <button
            key={i}
            onClick={() => onTogglePostSelection(i)}
            className={`p-3 rounded-lg border-2 transition-all ${
              selectedPosts.includes(i)
                ? 'bg-vitamin-base border-vitamin-base text-white'
                : 'bg-white/5 border-white/20 text-white/60 hover:border-white/40'
            }`}
          >
            {`Post ${i + 1}`}
          </button>
        ))}
      </div>

      <div className="flex gap-3">
        <Button
          onClick={onRegenerateSelectedPosts}
          disabled={regeneratingPosts || selectedPosts.length === 0}
          className="flex-1 bg-vitamin-base hover:bg-vitamin-700 text-white font-medium h-10 rounded-lg"
        >
          {regeneratingPosts ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              {t('postReview.regenerating', 'Regenerating...')}
            </>
          ) : (
            t('postReview.done', 'Done')
          )}
        </Button>
        <Button
          onClick={onCancelPostSelection}
          variant="outline"
          className="px-4 border-white/20 text-white hover:bg-white/10 h-10 rounded-lg"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </motion.div>
  )
}

function BottomActions({
  hasImages,
  onOpenFeedbackSurvey,
  onOpenNewPostsOptions,
}: {
  hasImages: boolean
  onOpenFeedbackSurvey: () => void
  onOpenNewPostsOptions: () => void
}) {
  const { t } = useTranslation()

  return (
    <div className="p-4 border-t border-white/10 bg-black/45 space-y-3 backdrop-blur-md">
      {hasImages && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-3"
        >
          <Button
            onClick={onOpenFeedbackSurvey}
            variant="outline"
            className="w-full border-white/20 text-black dark:text-white hover:bg-white/10 h-10 rounded-lg flex items-center justify-center gap-2"
          >
            <Star className="h-4 w-4" />
            {t('chat.feedbackSurvey', 'Feedback Survey')}
          </Button>

          <Button
            onClick={onOpenNewPostsOptions}
            variant="outline"
            className="w-full border-vitamin-base/30 text-vitamin-base hover:bg-vitamin-base/10 h-10 rounded-lg flex items-center justify-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            {t('chat.generateNewPosts', 'Generate New Posts and Images')}
          </Button>
        </motion.div>
      )}
    </div>
  )
}

function PanelTitle({
  icon,
  title,
  description,
}: {
  icon: ReactNode
  title: string
  description: string
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="p-2 rounded-lg bg-vitamin-base/15 text-vitamin-base shrink-0">{icon}</div>
      <div>
        <h4 className="text-sm font-bold text-white">{title}</h4>
        <p className="text-xs text-white/60 mt-1">{description}</p>
      </div>
    </div>
  )
}
