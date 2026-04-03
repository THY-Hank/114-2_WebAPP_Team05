import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Project, CodeFile, FileComment
from chat.models import ChatRoom
from user.models import CustomUser
from .user_views import login_check

@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_check
def project_list_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'error': 'Project name is required'}, status=400)
        
        new_project = Project.objects.create(name=name, owner=request.user)
        new_project.members.add(request.user)
        default_room = ChatRoom.objects.create(project=new_project, name='General')
        default_room.members.add(request.user)
        return JsonResponse({'id': new_project.id, 'name': new_project.name, 'owner_id': new_project.owner_id}, status=201)
    else:
        # GET is already handled by user/me/ mostly, but provided here as REST standard
        projects = [{'id': p.id, 'name': p.name, 'owner_id': p.owner_id} for p in request.user.projects.all()]
        return JsonResponse(projects, safe=False, status=200)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_check
def project_detail_view(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)
        
    if request.user != project.owner:
        return JsonResponse({'error': 'Only the owner can delete this project'}, status=403)
        
    project.delete()
    return HttpResponse(status=204)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_check
def file_detail_view(request, file_id):
    try:
        code_file = CodeFile.objects.get(id=file_id)
    except CodeFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
        
    if request.user not in code_file.project.members.all():
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    code_file.delete()
    return HttpResponse(status=204)

@csrf_exempt
@require_http_methods(["POST"])
@login_check
def add_project_member_view(request, project_id):
    try:
        project = Project.objects.get(id=project_id, members=request.user)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found or access denied'}, status=404)

    data = json.loads(request.body)
    email = data.get('email')
    if not email:
        return JsonResponse({'error': 'Email is required to invite a member'}, status=400)
    
    try:
        invited_user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': f'User with email {email} not found.'}, status=404)

    if project.members.filter(id=invited_user.id).exists():
        return JsonResponse({'error': 'User is already a member.'}, status=400)

    from .models import ProjectInvitation
    invitation, created = ProjectInvitation.objects.get_or_create(
        project=project,
        inviter=request.user,
        invitee=invited_user,
        status='pending'
    )
    return JsonResponse({'message': f'Invitation sent to {invited_user.name or invited_user.email}.'}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
@login_check
def invitation_list_view(request):
    from .models import ProjectInvitation
    invitations = ProjectInvitation.objects.filter(invitee=request.user, status='pending')
    data = []
    for inv in invitations:
        data.append({
            'id': inv.id,
            'project_name': inv.project.name,
            'inviter_name': inv.inviter.name or inv.inviter.email,
            'created_at': inv.created_at.isoformat()
        })
    return JsonResponse(data, safe=False, status=200)

@csrf_exempt
@require_http_methods(["POST"])
@login_check
def respond_invitation_view(request, invitation_id):
    from .models import ProjectInvitation
    try:
        invitation = ProjectInvitation.objects.get(id=invitation_id, invitee=request.user, status='pending')
    except ProjectInvitation.DoesNotExist:
        return JsonResponse({'error': 'Invitation not found or not pending'}, status=404)
        
    data = json.loads(request.body)
    action = data.get('action')
    
    if action == 'accept':
        invitation.status = 'accepted'
        invitation.project.members.add(request.user)
        for room in invitation.project.chatrooms.all():
            room.members.add(request.user)
        invitation.save()
        return JsonResponse({'status': 'accepted', 'project_id': invitation.project.id}, status=200)
    elif action == 'decline':
        invitation.status = 'declined'
        invitation.save()
        return JsonResponse({'status': 'declined'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)

@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_check
def project_files_view(request, project_id):
    try:
        project = Project.objects.get(id=project_id, members=request.user)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found or access denied'}, status=404)

    if request.method == "GET":
        files_data = []
        for file in project.files.all():
            comments = [{
                'id': c.id,
                'author': c.author.name or c.author.email,
                'text': c.text
            } for c in file.comments.all()]
            
            files_data.append({
                'id': file.id,
                'projectId': project.id,
                'name': file.name,
                'filepath': file.filepath,
                'content': file.content,
                'comments': comments
            })
        return JsonResponse(files_data, safe=False, status=200)

    elif request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        filepath = data.get('filepath', '')  # Get filepath from request, default to empty
        content = data.get('content', '')
        if not name:
            return JsonResponse({'error': 'File name is required'}, status=400)
            
        new_file = CodeFile.objects.create(project=project, name=name, filepath=filepath, content=content)
        return JsonResponse({'id': new_file.id, 'name': new_file.name, 'filepath': new_file.filepath, 'content': new_file.content, 'comments': []}, status=201)

@csrf_exempt
@require_http_methods(["POST"])
@login_check
def add_file_comment_view(request, file_id):
    try:
        code_file = CodeFile.objects.get(id=file_id, project__members=request.user)
    except CodeFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)

    data = json.loads(request.body)
    text = data.get('text')
    if not text:
        return JsonResponse({'error': 'Comment text is required'}, status=400)
        
    comment = FileComment.objects.create(file=code_file, author=request.user, text=text)
    return JsonResponse({
        'id': comment.id,
        'author': request.user.name or request.user.email,
        'text': comment.text
    }, status=201)

@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_check
def line_comments_view(request, file_id):
    """Get or create line-level comments on a specific file"""
    try:
        code_file = CodeFile.objects.get(id=file_id, project__members=request.user)
    except CodeFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)

    if request.method == "GET":
        # Return all line-level comments for this file
        comments_data = []
        for comment in code_file.comments.filter(comment_type='line'):
            comments_data.append({
                'id': comment.id,
                'author': comment.author.name or comment.author.email,
                'text': comment.text,
                'startLine': comment.start_line,
                'endLine': comment.end_line,
                'createdAt': comment.created_at.isoformat()
            })
        return JsonResponse(comments_data, safe=False, status=200)

    elif request.method == "POST":
        data = json.loads(request.body)
        text = data.get('text')
        start_line = data.get('startLine')
        end_line = data.get('endLine')
        
        if not text or start_line is None:
            return JsonResponse({'error': 'Text and startLine are required'}, status=400)
        
        if end_line is None:
            end_line = start_line
        
        comment = FileComment.objects.create(
            file=code_file,
            author=request.user,
            text=text,
            comment_type='line',
            start_line=start_line,
            end_line=end_line
        )
        return JsonResponse({
            'id': comment.id,
            'author': request.user.name or request.user.email,
            'text': comment.text,
            'startLine': comment.start_line,
            'endLine': comment.end_line,
            'createdAt': comment.created_at.isoformat()
        }, status=201)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
@login_check
def project_settings_view(request, project_id):
    """Manage project settings: get/update name, get members, remove members"""
    try:
        project = Project.objects.get(id=project_id, members=request.user)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found or access denied'}, status=404)

    if request.method == "GET":
        # Return project info and members list
        members_data = []
        for member in project.members.all():
            members_data.append({
                'id': member.id,
                'name': member.name or member.email,
                'email': member.email,
                'isOwner': project.owner_id == member.id,
                'joinedAt': member.date_joined.isoformat() if hasattr(member, 'date_joined') else None
            })
        return JsonResponse({
            'id': project.id,
            'name': project.name,
            'owner_id': project.owner_id,
            'members': members_data,
            'isOwner': request.user.id == project.owner_id
        }, status=200)

    elif request.method == "PUT":
        # Update project name (owner only)
        if request.user.id != project.owner_id:
            return JsonResponse({'error': 'Only the owner can update project settings'}, status=403)
        
        data = json.loads(request.body)
        new_name = data.get('name')
        if not new_name:
            return JsonResponse({'error': 'Project name is required'}, status=400)
        
        project.name = new_name
        project.save()
        return JsonResponse({'message': 'Project updated successfully', 'name': project.name}, status=200)

    elif request.method == "DELETE":
        # Remove a member from the project
        if request.user.id != project.owner_id:
            return JsonResponse({'error': 'Only the owner can remove members'}, status=403)
        
        data = json.loads(request.body)
        member_id = data.get('member_id')
        if not member_id:
            return JsonResponse({'error': 'member_id is required'}, status=400)
        
        try:
            member_to_remove = CustomUser.objects.get(id=member_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Member not found'}, status=404)
        
        if member_to_remove.id == project.owner_id:
            return JsonResponse({'error': 'Cannot remove the project owner'}, status=400)
        
        if not project.members.filter(id=member_id).exists():
            return JsonResponse({'error': 'User is not a member of this project'}, status=400)
        
        project.members.remove(member_to_remove)
        # Also remove from all chat rooms in this project
        for room in project.chatrooms.all():
            room.members.remove(member_to_remove)
        
        return JsonResponse({'message': f'Member removed successfully'}, status=200)
