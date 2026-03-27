import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatRoom, ChatMessage
from .user_views import login_check

@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_check
def chatrooms_view(request):
    if request.method == "GET":
        rooms = ChatRoom.objects.all()
        rooms_data = []
        for room in rooms:
            messages = []
            for m in room.messages.all():
                msg_payload = {
                    'id': m.id,
                    'author': m.author.name or m.author.email,
                }
                if m.text:
                    msg_payload['text'] = m.text
                if m.code_snippet_file:
                    msg_payload['codeSnippet'] = {
                        'fileName': m.code_snippet_file,
                        'line': m.code_snippet_line
                    }
                messages.append(msg_payload)
            rooms_data.append({
                'id': room.id,
                'name': room.name,
                'messages': messages
            })
        return JsonResponse(rooms_data, safe=False, status=200)

    elif request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'error': 'Room name is required'}, status=400)
            
        new_room = ChatRoom.objects.create(name=name)
        new_room.members.add(request.user)
        return JsonResponse({'id': new_room.id, 'name': new_room.name, 'messages': []}, status=201)

@csrf_exempt
@require_http_methods(["POST"])
@login_check
def add_chat_message_view(request, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

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

    response_payload = {
        'id': msg.id,
        'author': msg.author.name or msg.author.email,
    }
    if text:
        response_payload['text'] = msg.text
    if snippet_file:
        response_payload['codeSnippet'] = {
            'fileName': msg.code_snippet_file,
            'line': msg.code_snippet_line
        }
    return JsonResponse(response_payload, status=201)
