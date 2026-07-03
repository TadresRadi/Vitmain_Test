from django.urls import path
from chat.views import (
    PremiumPostsView,
    ModifyPostsView,
    GenerateImagesView,
    RegenerateSelectedPostsView,
    CompletePostReviewView,
    PostsHistoryView,
    ImagesOnlyHistoryView,
)
from chat.views.images_history_view import ImagesHistoryView

urlpatterns = [
    path('chat/premium-posts', PremiumPostsView.as_view(), name='premium_posts'),
    path('chat/modify-posts', ModifyPostsView.as_view(), name='modify_posts'),
    path('chat/generate-images', GenerateImagesView.as_view(), name='generate_images'),
    path('chat/regenerate-selected-posts', RegenerateSelectedPostsView.as_view(), name='regenerate_selected_posts'),
    path('chat/complete-post-review', CompletePostReviewView.as_view(), name='complete_post_review'),
    path('images/history', ImagesHistoryView.as_view(), name='images_history'),
    path('posts/history', PostsHistoryView.as_view(), name='posts_history'),
    path('images/only-history', ImagesOnlyHistoryView.as_view(), name='images_only_history'),
]
