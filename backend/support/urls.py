from django.urls import path
from support.views import UserSupportChatView, AdminSupportChatListView, AdminSupportChatReplyView

urlpatterns = [
    path('support/chat', UserSupportChatView.as_view(), name='user_support_chat'),
    path('admin/support/chats', AdminSupportChatListView.as_view(), name='admin_support_chats'),
    path('admin/support/reply', AdminSupportChatReplyView.as_view(), name='admin_support_reply'),
]
