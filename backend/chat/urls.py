from django.urls import path
from . import views

urlpatterns = [
    path('<int:project_id>/chatrooms/', views.project_chatrooms_view, name='api_project_chatrooms'),
    path('<int:project_id>/chatrooms/<int:room_id>/', views.chatroom_detail_view, name='api_chatroom_detail'),
    path('<int:project_id>/chatrooms/<int:room_id>/messages/', views.add_chat_message_view, name='api_add_chat_message'),
    path('<int:project_id>/chatrooms/<int:room_id>/read/', views.mark_chatroom_read_view, name='api_mark_chatroom_read'),
    path('<int:project_id>/chatrooms/<int:room_id>/messages/<int:message_id>/pin/', views.pin_chat_message_view, name='api_pin_chat_message'),
]
