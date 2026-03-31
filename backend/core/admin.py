from django.contrib import admin

from .models import CodeFile, FileComment, Project, ProjectInvitation


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



@admin.register(ProjectInvitation)
class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'inviter', 'invitee', 'status', 'created_at')
    list_filter = ('status',)
