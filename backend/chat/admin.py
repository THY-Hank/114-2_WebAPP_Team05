from django.contrib import admin
from .models import ChatMessage, ChatRoom

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    filter_horizontal = ('members',)
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'author', 'text', 'code_snippet_file', 'created_at')
    list_filter = ('room', 'author')
