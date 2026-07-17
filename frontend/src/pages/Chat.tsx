import DashboardLayout from '@/components/DashboardLayout'
import { CampaignStudioPanel } from '@/pages/chat/CampaignStudioPanel'
import { ChatPageHeader } from '@/pages/chat/ChatPageHeader'
import { FeedbackSurveyModal } from '@/pages/chat/FeedbackSurveyModal'
import { NewPostsOptionsModal } from '@/pages/chat/NewPostsOptionsModal'
import { useChatController } from '@/pages/chat/useChatController'

export default function Chat() {
  const chat = useChatController()

  return (
    <DashboardLayout>
      <div className="flex flex-col h-screen overflow-hidden">
        <ChatPageHeader />

        <CampaignStudioPanel
          loading={chat.loading}
          postGen={chat.postGen}
          postsWithImages={chat.postsWithImages}
          generatingPosts={chat.generatingPosts}
          generatingImages={chat.generatingImages}
          showPostReview={chat.showPostReview}
          showPostSelection={chat.showPostSelection}
          selectedPosts={chat.selectedPosts}
          regeneratingPosts={chat.regeneratingPosts}
          onGeneratePosts={() => chat.handleGeneratePosts()}
          onGenerateImages={chat.handleGenerateImages}
          onPostReviewYes={chat.handlePostReviewYes}
          onPostReviewNo={chat.handlePostReviewNo}
          onRegenerateSelectedPosts={chat.handleRegenerateSelectedPosts}
          onTogglePostSelection={chat.togglePostSelection}
          onCancelPostSelection={chat.resetPostSelection}
          onOpenFeedbackSurvey={() => chat.setShowFeedbackSurvey(true)}
          onOpenNewPostsOptions={() => chat.setShowNewPostsOptions(true)}
        />

        <FeedbackSurveyModal
          open={chat.showFeedbackSurvey}
          submitted={chat.feedbackSubmitted}
          feedbackData={chat.feedbackData}
          setFeedbackData={chat.setFeedbackData}
          onClose={() => chat.setShowFeedbackSurvey(false)}
          onSubmit={chat.handleFeedbackSubmit}
        />

        <NewPostsOptionsModal
          open={chat.showNewPostsOptions}
          onClose={() => chat.setShowNewPostsOptions(false)}
          onUseNewBusinessInfo={chat.handleUseNewBusinessInfo}
          onUseExistingBusinessInfo={chat.handleUseExistingBusinessInfo}
        />
      </div>
    </DashboardLayout>
  )
}
