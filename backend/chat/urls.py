from django.urls import path
from . import views

urlpatterns = [
    path('<int:project_id>/chatrooms/', views.project_chatrooms_view, name='api_project_chatrooms'),
    path('<int:project_id>/chatrooms/<int:room_id>/messages/', views.add_chat_message_view, name='api_add_chat_message'),
]
