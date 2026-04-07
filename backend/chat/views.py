import json
import re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ChatRoom, ChatMessage, ChatReadState
from core.models import Project
from core.user_views import login_check


MENTION_PATTERN = re.compile(r'@([A-Za-z0-9._-]+)')


def _get_room_member_map(room):
    return {
        member.id: {
            'display': member.name or member.email,
            'tokens': {
                (member.name or '').strip().lower(),
                member.email.split('@')[0].lower(),
                member.email.lower(),
            }
        }
        for member in room.members.all()
    }


def _extract_mentions(room, text):
    if not text:
        return []

    member_map = _get_room_member_map(room)
    mentions = []
    seen = set()
    for raw_token in MENTION_PATTERN.findall(text):
        token = raw_token.lower()
        for member_id, member_info in member_map.items():
            normalized_tokens = {value for value in member_info['tokens'] if value}
            if token in normalized_tokens and member_id not in seen:
                mentions.append({
                    'userId': member_id,
                    'label': member_info['display'],
                    'token': raw_token,
                })
                seen.add(member_id)
                break
    return mentions


def _get_latest_message(room):
    return room.messages.order_by('-created_at', '-id').first()


def _get_unread_count(room, user):
    if not user.is_authenticated:
        return 0

    read_state = ChatReadState.objects.filter(room=room, user=user).select_related('last_read_message').first()
    if not read_state or not read_state.last_read_message_id:
        return room.messages.exclude(author=user).count()

    last_message = read_state.last_read_message
    return room.messages.filter(id__gt=last_message.id).exclude(author=user).count()


def _serialize_message(message, current_user=None):
    room = message.room
    read_by_count = room.read_states.filter(last_read_message_id__gte=message.id).count()
    payload = {
        'id': message.id,
        'author': message.author.name or message.author.email,
        'createdAt': message.created_at.isoformat(),
        'isPinned': message.is_pinned,
        'mentions': _extract_mentions(room, message.text),
        'readByCount': read_by_count,
        'isReadByCurrentUser': bool(
            current_user
            and current_user.is_authenticated
            and room.read_states.filter(user=current_user, last_read_message_id__gte=message.id).exists()
        ),
    }
    if message.text:
        payload['text'] = message.text
    if message.code_snippet_file:
        payload['codeSnippet'] = {
            'fileName': message.code_snippet_file,
            'line': message.code_snippet_line,
            'startLine': message.code_snippet_start_line,
            'endLine': message.code_snippet_end_line,
            'content': message.code_snippet_content
        }
    return payload


def _serialize_room(room, current_user=None):
    latest_message = _get_latest_message(room)
    return {
        'id': room.id,
        'projectId': room.project_id,
        'name': room.name,
        'createdBy': room.created_by.name if room.created_by and room.created_by.name else (room.created_by.email if room.created_by else None),
        'unreadCount': _get_unread_count(room, current_user) if current_user else 0,
        'lastMessageAt': latest_message.created_at.isoformat() if latest_message else None,
        'messages': [
            _serialize_message(message, current_user=current_user)
            for message in room.messages.all().order_by('created_at', 'id')
        ]
    }


def _room_for_member(project_id, room_id, user):
    return ChatRoom.objects.filter(
        id=room_id,
        project_id=project_id,
        members=user,
    ).prefetch_related('members', 'messages__author', 'read_states').first()


def _broadcast_room_event(room_id, payload):
    event_type = 'chat_message' if payload.get('action') == 'new_message' else 'chat_event'
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{room_id}',
        {
            'type': event_type,
            'payload': payload
        }
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_check
def project_chatrooms_view(request, project_id):
    try:
        project = Project.objects.get(id=project_id, members=request.user)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found or access denied'}, status=404)

    if request.method == "GET":
        rooms = ChatRoom.objects.filter(project=project, members=request.user).prefetch_related(
            'members', 'messages__author', 'read_states', 'created_by'
        ).order_by('created_at', 'id')
        rooms_data = [_serialize_room(room, current_user=request.user) for room in rooms]
        return JsonResponse(rooms_data, safe=False, status=200)

    data = json.loads(request.body)
    name = data.get('name')
    if not name:
        return JsonResponse({'error': 'Room name is required'}, status=400)

    new_room = ChatRoom.objects.create(name=name, project=project, created_by=request.user)

    member_ids = data.get('memberIds')
    if member_ids and isinstance(member_ids, list):
        valid_member_ids = list(project.members.filter(id__in=member_ids).values_list('id', flat=True))
        if request.user.id not in valid_member_ids:
            valid_member_ids.append(request.user.id)
        new_room.members.set(valid_member_ids)
    else:
        new_room.members.set(project.members.all())

    ChatReadState.objects.get_or_create(room=new_room, user=request.user)
    return JsonResponse(_serialize_room(new_room, current_user=request.user), status=201)


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
@login_check
def chatroom_detail_view(request, project_id, room_id):
    room = _room_for_member(project_id, room_id, request.user)
    if not room:
        return JsonResponse({'error': 'Room not found or access denied'}, status=404)

    is_owner = room.project and room.project.owner_id == request.user.id
    is_creator = room.created_by_id == request.user.id
    if not (is_owner or is_creator):
        return JsonResponse({'error': 'Only the room creator or project owner can manage this room'}, status=403)

    if request.method == "PUT":
        data = json.loads(request.body)
        name = (data.get('name') or '').strip()
        if not name:
            return JsonResponse({'error': 'Room name is required'}, status=400)
        room.name = name
        room.save(update_fields=['name'])
        return JsonResponse(_serialize_room(room, current_user=request.user), status=200)

    if room.name == 'General':
        return JsonResponse({'error': 'The default room cannot be deleted'}, status=400)

    room.delete()
    return HttpResponse(status=204)


@csrf_exempt
@require_http_methods(["POST"])
@login_check
def add_chat_message_view(request, project_id, room_id):
    room = _room_for_member(project_id, room_id, request.user)
    if not room:
        return JsonResponse({'error': 'Room not found or access denied'}, status=404)

    data = json.loads(request.body)
    text = data.get('text')
    snippet_file = data.get('codeSnippetFile')
    snippet_line = data.get('codeSnippetLine')
    snippet_start_line = data.get('codeSnippetStartLine')
    snippet_end_line = data.get('codeSnippetEndLine')
    snippet_content = data.get('codeSnippetContent')

    if not text and not snippet_file:
        return JsonResponse({'error': 'Message content or code snippet required'}, status=400)

    msg = ChatMessage.objects.create(
        room=room,
        author=request.user,
        text=text,
        code_snippet_file=snippet_file,
        code_snippet_line=snippet_line,
        code_snippet_start_line=snippet_start_line,
        code_snippet_end_line=snippet_end_line,
        code_snippet_content=snippet_content
    )

    ChatReadState.objects.update_or_create(
        room=room,
        user=request.user,
        defaults={'last_read_message': msg},
    )

    payload = _serialize_message(msg, current_user=request.user)
    _broadcast_room_event(room.id, {'action': 'new_message', 'payload': payload})
    return JsonResponse(payload, status=201)


@csrf_exempt
@require_http_methods(["POST"])
@login_check
def mark_chatroom_read_view(request, project_id, room_id):
    room = _room_for_member(project_id, room_id, request.user)
    if not room:
        return JsonResponse({'error': 'Room not found or access denied'}, status=404)

    latest_message = _get_latest_message(room)
    read_state, _ = ChatReadState.objects.get_or_create(room=room, user=request.user)
    read_state.last_read_message = latest_message
    read_state.save(update_fields=['last_read_message', 'updated_at'])

    return JsonResponse({
        'roomId': room.id,
        'unreadCount': 0,
        'lastReadMessageId': latest_message.id if latest_message else None,
    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
@login_check
def pin_chat_message_view(request, project_id, room_id, message_id):
    room = _room_for_member(project_id, room_id, request.user)
    if not room:
        return JsonResponse({'error': 'Room not found or access denied'}, status=404)

    try:
        message = room.messages.get(id=message_id)
    except ChatMessage.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)

    is_owner = room.project and room.project.owner_id == request.user.id
    can_manage = is_owner or message.author_id == request.user.id or room.created_by_id == request.user.id
    if not can_manage:
        return JsonResponse({'error': 'Only the author, room creator, or project owner can pin messages'}, status=403)

    data = json.loads(request.body) if request.body else {}
    desired_state = data.get('isPinned')
    message.is_pinned = (not message.is_pinned) if desired_state is None else bool(desired_state)
    message.save(update_fields=['is_pinned'])

    payload = _serialize_message(message, current_user=request.user)
    _broadcast_room_event(room.id, {'action': 'message_updated', 'payload': payload})
    return JsonResponse(payload, status=200)
