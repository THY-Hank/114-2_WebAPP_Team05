from django.urls import path
from . import user_views, project_views, chat_views

urlpatterns = [
    path('user/me/', user_views.me_view, name='api_me'),
    path('projects/', project_views.project_list_view, name='api_projects'),
    path('projects/<int:project_id>/', project_views.project_detail_view, name='api_project_detail'),
    path('projects/<int:project_id>/members/', project_views.add_project_member_view, name='api_project_members'),
    path('projects/<int:project_id>/files/', project_views.project_files_view, name='api_project_files'),
    path('files/<int:file_id>/', project_views.file_detail_view, name='api_file_detail'),
    path('files/<int:file_id>/comments/', project_views.add_file_comment_view, name='api_add_file_comment'),
    path('invitations/', project_views.invitation_list_view, name='api_invitation_list'),
    path('invitations/<int:invitation_id>/respond/', project_views.respond_invitation_view, name='api_invitation_respond'),
    path('chatrooms/', chat_views.chatrooms_view, name='api_chatrooms'),
    path('chatrooms/<int:room_id>/messages/', chat_views.add_chat_message_view, name='api_add_chat_message'),
]
