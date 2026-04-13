import json
import re
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

from .models import ChatRoom, ChatMessage, ChatReadState, ChatNotification
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


def _serialize_member(member):
    return {
        'id': member.id,
        'name': member.name or member.email.split('@')[0],
        'email': member.email,
    }


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
        'authorId': message.author_id,
        'author': message.author.name or message.author.email,
        'createdAt': message.created_at.isoformat(),
        'isPinned': message.is_pinned,
        'isDeleted': message.deleted_at is not None,
        'editedAt': message.edited_at.isoformat() if message.edited_at else None,
        'mentions': _extract_mentions(room, message.text),
        'readByCount': read_by_count,
        'isReadByCurrentUser': bool(
            current_user
            and current_user.is_authenticated
            and room.read_states.filter(user=current_user, last_read_message_id__gte=message.id).exists()
        ),
    }
    if message.reply_to_id:
        payload['replyTo'] = {
            'id': message.reply_to_id,
            'author': message.reply_to.author.name or message.reply_to.author.email,
            'text': (message.reply_to.text or '').strip()[:120] or ('[Attachment]' if message.reply_to.attachment else '[Snippet]'),
        }
    if message.deleted_at:
        payload['text'] = 'This message was deleted.'
        return payload
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
    if message.attachment:
        payload['attachment'] = {
            'name': message.attachment_name or os.path.basename(message.attachment.name),
            'url': message.attachment.url,
            'contentType': message.attachment_content_type or '',
            'isImage': (message.attachment_content_type or '').startswith('image/'),
        }
    return payload


def _serialize_notification(notification):
    return {
        'id': notification.id,
        'type': notification.notification_type,
        'text': notification.text,
        'isRead': notification.is_read,
        'createdAt': notification.created_at.isoformat(),
        'roomId': notification.room_id,
        'messageId': notification.message_id,
        'projectId': notification.room.project_id if notification.room_id else None,
    }


def _serialize_room(room, current_user=None):
    latest_message = _get_latest_message(room)
    return {
        'id': room.id,
        'projectId': room.project_id,
        'name': room.name,
        'createdBy': room.created_by.name if room.created_by and room.created_by.name else (room.created_by.email if room.created_by else None),
        'unreadCount': _get_unread_count(room, current_user) if current_user else 0,
        'lastMessageAt': latest_message.created_at.isoformat() if latest_message else None,
        'members': [_serialize_member(member) for member in room.members.all()],
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


def _broadcast_notification(user_id, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'notification_event',
            'payload': payload,
        }
    )


def _create_notification(*, user, notification_type, text, room=None, message=None):
    notification = ChatNotification.objects.create(
        user=user,
        room=room,
        message=message,
        notification_type=notification_type,
        text=text,
    )
    _broadcast_notification(user.id, {
        'action': 'notification_created',
        'payload': _serialize_notification(notification),
    })
    return notification


def _notify_for_message(message):
    room = message.room
    actor_label = message.author.name or message.author.email
    mentioned_user_ids = {mention['userId'] for mention in _extract_mentions(room, message.text)}
    for user_id in mentioned_user_ids:
        if user_id == message.author_id:
            continue
        user = room.members.filter(id=user_id).first()
        if user:
            _create_notification(
                user=user,
                notification_type='mention',
                text=f'{actor_label} mentioned you in {room.name}',
                room=room,
                message=message,
            )

    if message.reply_to_id and message.reply_to.author_id != message.author_id:
        _create_notification(
            user=message.reply_to.author,
            notification_type='reply',
            text=f'{actor_label} replied to your message in {room.name}',
            room=room,
            message=message,
        )


def _parse_message_request(request):
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        return {
            'text': request.POST.get('text'),
            'codeSnippetFile': request.POST.get('codeSnippetFile'),
            'codeSnippetLine': request.POST.get('codeSnippetLine'),
            'codeSnippetStartLine': request.POST.get('codeSnippetStartLine'),
            'codeSnippetEndLine': request.POST.get('codeSnippetEndLine'),
            'codeSnippetContent': request.POST.get('codeSnippetContent'),
            'replyToMessageId': request.POST.get('replyToMessageId'),
            'attachment': request.FILES.get('attachment'),
        }
    return json.loads(request.body or '{}')


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
    for member in new_room.members.exclude(id=request.user.id):
        _create_notification(
            user=member,
            notification_type='room_invite',
            text=f'You were added to room "{new_room.name}" in {project.name}',
            room=new_room,
        )
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

    data = _parse_message_request(request)
    text = data.get('text')
    snippet_file = data.get('codeSnippetFile')
    snippet_line = data.get('codeSnippetLine')
    snippet_start_line = data.get('codeSnippetStartLine')
    snippet_end_line = data.get('codeSnippetEndLine')
    snippet_content = data.get('codeSnippetContent')
    reply_to_message_id = data.get('replyToMessageId')
    attachment = data.get('attachment')

    if not text and not snippet_file and not attachment:
        return JsonResponse({'error': 'Message content or code snippet required'}, status=400)

    reply_to = None
    if reply_to_message_id:
        reply_to = room.messages.filter(id=reply_to_message_id).select_related('author').first()
        if reply_to is None:
            return JsonResponse({'error': 'Reply target not found'}, status=404)

    msg = ChatMessage.objects.create(
        room=room,
        author=request.user,
        text=text,
        reply_to=reply_to,
        code_snippet_file=snippet_file,
        code_snippet_line=int(snippet_line) if snippet_line else None,
        code_snippet_start_line=int(snippet_start_line) if snippet_start_line else None,
        code_snippet_end_line=int(snippet_end_line) if snippet_end_line else None,
        code_snippet_content=snippet_content,
        attachment=attachment if attachment else None,
        attachment_name=attachment.name if attachment else None,
        attachment_content_type=getattr(attachment, 'content_type', '') if attachment else '',
    )

    ChatReadState.objects.update_or_create(
        room=room,
        user=request.user,
        defaults={'last_read_message': msg},
    )

    payload = _serialize_message(msg, current_user=request.user)
    _notify_for_message(msg)
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


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
@login_check
def chat_message_detail_view(request, project_id, room_id, message_id):
    room = _room_for_member(project_id, room_id, request.user)
    if not room:
        return JsonResponse({'error': 'Room not found or access denied'}, status=404)

    try:
        message = room.messages.select_related('reply_to__author').get(id=message_id)
    except ChatMessage.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)

    is_owner = room.project and room.project.owner_id == request.user.id
    can_manage = is_owner or message.author_id == request.user.id or room.created_by_id == request.user.id
    if not can_manage:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == "PUT":
        data = json.loads(request.body or '{}')
        text = (data.get('text') or '').strip()
        if not text and not message.code_snippet_file and not message.attachment:
            return JsonResponse({'error': 'Message text cannot be empty'}, status=400)
        message.text = text or None
        message.edited_at = timezone.now()
        message.save(update_fields=['text', 'edited_at'])
        payload = _serialize_message(message, current_user=request.user)
        _broadcast_room_event(room.id, {'action': 'message_updated', 'payload': payload})
        return JsonResponse(payload, status=200)

    message.text = None
    message.code_snippet_file = None
    message.code_snippet_line = None
    message.code_snippet_start_line = None
    message.code_snippet_end_line = None
    message.code_snippet_content = None
    if message.attachment:
        message.attachment.delete(save=False)
    message.attachment = None
    message.attachment_name = None
    message.attachment_content_type = None
    message.deleted_at = timezone.now()
    message.save(update_fields=[
        'text',
        'code_snippet_file',
        'code_snippet_line',
        'code_snippet_start_line',
        'code_snippet_end_line',
        'code_snippet_content',
        'attachment',
        'attachment_name',
        'attachment_content_type',
        'deleted_at',
    ])
    payload = _serialize_message(message, current_user=request.user)
    _broadcast_room_event(room.id, {'action': 'message_updated', 'payload': payload})
    return HttpResponse(status=204)


@csrf_exempt
@require_http_methods(["GET"])
@login_check
def notification_list_view(request):
    notifications = ChatNotification.objects.filter(user=request.user).select_related('room', 'message')[:50]
    return JsonResponse([_serialize_notification(notification) for notification in notifications], safe=False, status=200)


@csrf_exempt
@require_http_methods(["POST"])
@login_check
def notification_mark_read_view(request, notification_id):
    try:
        notification = ChatNotification.objects.get(id=notification_id, user=request.user)
    except ChatNotification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return JsonResponse(_serialize_notification(notification), status=200)
