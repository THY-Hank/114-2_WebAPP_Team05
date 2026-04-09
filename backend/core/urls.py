from django.urls import path
from . import user_views, project_views

urlpatterns = [
    path('user/me/', user_views.me_view, name='api_me'),
    path('projects/', project_views.project_list_view, name='api_projects'),
    path('projects/<int:project_id>/', project_views.project_detail_view, name='api_project_detail'),
    path('projects/<int:project_id>/settings/', project_views.project_settings_view, name='api_project_settings'),
    path('projects/<int:project_id>/members/', project_views.add_project_member_view, name='api_project_members'),
    path('projects/<int:project_id>/files/', project_views.project_files_view, name='api_project_files'),
    path('files/<int:file_id>/', project_views.file_detail_view, name='api_file_detail'),
    path('files/<int:file_id>/content/', project_views.update_file_content_view, name='api_update_file_content'),
    path('files/<int:file_id>/versions/', project_views.file_versions_view, name='api_file_versions'),
    path('files/<int:file_id>/versions/diff/', project_views.file_versions_diff_view, name='api_file_versions_diff'),
    path('files/<int:file_id>/versions/<int:version_id>/snapshot/', project_views.file_version_snapshot_view, name='api_file_version_snapshot'),
    path('files/<int:file_id>/revert/', project_views.file_revert_view, name='api_file_revert'),
    path('files/<int:file_id>/comments/', project_views.add_file_comment_view, name='api_add_file_comment'),
    path('files/<int:file_id>/line-comments/', project_views.line_comments_view, name='api_line_comments'),
    path('invitations/', project_views.invitation_list_view, name='api_invitation_list'),
    path('invitations/<int:invitation_id>/respond/', project_views.respond_invitation_view, name='api_invitation_respond'),
]
