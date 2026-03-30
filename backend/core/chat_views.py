import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatRoom, ChatMessage, Project
from .user_views import login_check


def _serialize_message(message):
    payload = {
        'id': message.id,
        'author': message.author.name or message.author.email,
        'createdAt': message.created_at.isoformat(),
    }
    if message.text:
        payload['text'] = message.text
    if message.code_snippet_file:
        payload['codeSnippet'] = {
            'fileName': message.code_snippet_file,
            'line': message.code_snippet_line
        }
    return payload


def _serialize_room(room):
    return {
        'id': room.id,
        'projectId': room.project_id,
        'name': room.name,
        'messages': [_serialize_message(message) for message in room.messages.all().order_by('created_at', 'id')]
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_check
def project_chatrooms_view(request, project_id):
    try:
        project = Project.objects.get(id=project_id, members=request.user)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found or access denied'}, status=404)

    if request.method == "GET":
        rooms = ChatRoom.objects.filter(project=project).prefetch_related('messages__author').order_by('created_at', 'id')
        rooms_data = [_serialize_room(room) for room in rooms]
        return JsonResponse(rooms_data, safe=False, status=200)

    elif request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'error': 'Room name is required'}, status=400)
            
        new_room = ChatRoom.objects.create(name=name, project=project)
        new_room.members.set(project.members.all())
        return JsonResponse(_serialize_room(new_room), status=201)

@csrf_exempt
@require_http_methods(["POST"])
@login_check
def add_chat_message_view(request, project_id, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id, project_id=project_id, project__members=request.user)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'error': 'Room not found or access denied'}, status=404)

    data = json.loads(request.body)
    text = data.get('text')
    snippet_file = data.get('codeSnippetFile')
    snippet_line = data.get('codeSnippetLine')

    if not text and not snippet_file:
        return JsonResponse({'error': 'Message content or code snippet required'}, status=400)

    msg = ChatMessage.objects.create(
        room=room, 
        author=request.user, 
        text=text, 
        code_snippet_file=snippet_file, 
        code_snippet_line=snippet_line
    )

    return JsonResponse(_serialize_message(msg), status=201)
