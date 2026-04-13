from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class ChatRoom(models.Model):
    project = models.ForeignKey('core.Project', on_delete=models.CASCADE, related_name='chatrooms', null=True, blank=True)
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='chatrooms', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_chatrooms', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.project_id:
            return f"{self.project.name} - {self.name}"
        return self.name

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    code_snippet_file = models.CharField(max_length=255, blank=True, null=True)
    code_snippet_line = models.IntegerField(blank=True, null=True)
    code_snippet_start_line = models.IntegerField(blank=True, null=True)  # For line range sharing
    code_snippet_end_line = models.IntegerField(blank=True, null=True)    # For multi-line sharing
    code_snippet_content = models.TextField(blank=True, null=True)  # Preview of shared code
    attachment = models.FileField(upload_to='chat_attachments/%Y/%m/%d/', blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment_content_type = models.CharField(max_length=255, blank=True, null=True)
    edited_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.author} in {self.room.name}"


class ChatReadState(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='read_states')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_read_states')
    last_read_message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('room', 'user')

    def __str__(self):
        return f"{self.user} read {self.room}"


class ChatNotification(models.Model):
    TYPE_CHOICES = (
        ('mention', 'Mention'),
        ('reply', 'Reply'),
        ('room_invite', 'Room Invite'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_notifications')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"{self.user} - {self.notification_type}"
