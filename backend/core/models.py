from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Project(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects', null=True, blank=True)
    members = models.ManyToManyField(User, related_name='projects')

    def __str__(self):
        return self.name

class CodeFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    filepath = models.CharField(max_length=500, default='', blank=True)  # e.g., "src/components/button.vue"
    content = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class FileComment(models.Model):
    COMMENT_TYPE_CHOICES = (
        ('file', 'Whole File'),
        ('line', 'Line Range')
    )
    
    file = models.ForeignKey(CodeFile, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    comment_type = models.CharField(max_length=10, choices=COMMENT_TYPE_CHOICES, default='file')
    start_line = models.IntegerField(null=True, blank=True)  # For line comments
    end_line = models.IntegerField(null=True, blank=True)    # For multi-line comments
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.comment_type == 'line':
            return f"Line {self.start_line}-{self.end_line} comment by {self.author} on {self.file.name}"
        return f"Comment by {self.author} on {self.file.name}"



class ProjectInvitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inviter} invited {self.invitee} to {self.project.name} ({self.status})"
