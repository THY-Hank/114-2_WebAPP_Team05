from django.contrib import admin

from .models import ChatMessage, ChatRoom, CodeFile, FileComment, Project, ProjectInvitation


class CodeFileInline(admin.TabularInline):
    model = CodeFile
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner')
    filter_horizontal = ('members',)
    inlines = [CodeFileInline]


@admin.register(CodeFile)
class CodeFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'uploaded_at')
    list_filter = ('project',)


@admin.register(FileComment)
class FileCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'author', 'created_at')
    list_filter = ('author',)


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


@admin.register(ProjectInvitation)
class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'inviter', 'invitee', 'status', 'created_at')
    list_filter = ('status',)
