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
    code_snippet_file = models.CharField(max_length=255, blank=True, null=True)
    code_snippet_line = models.IntegerField(blank=True, null=True)
    code_snippet_start_line = models.IntegerField(blank=True, null=True)  # For line range sharing
    code_snippet_end_line = models.IntegerField(blank=True, null=True)    # For multi-line sharing
    code_snippet_content = models.TextField(blank=True, null=True)  # Preview of shared code
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
