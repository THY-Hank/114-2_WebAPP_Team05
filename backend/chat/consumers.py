import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from user.jwt_utils import get_user_from_token


@database_sync_to_async
def _resolve_user(scope):
    scope_user = scope.get('user')
    if scope_user is not None and getattr(scope_user, 'is_authenticated', False):
        return scope_user

    query_string = (scope.get('query_string') or b'').decode('utf-8')
    token = parse_qs(query_string).get('token', [None])[0]
    if not token:
        return None
    return get_user_from_token(token)


@database_sync_to_async
def _can_access_room(user, room_id):
    if user is None:
        return True

    if not user.is_authenticated:
        return False

    from .models import ChatRoom
    return ChatRoom.objects.filter(id=room_id, members=user).exists()

class ChatConsumer(AsyncWebsocketConsumer):
    room_presence = {}

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        resolved_user = await _resolve_user(self.scope)
        self.scope['resolved_user'] = resolved_user

        if not await _can_access_room(resolved_user, self.room_id):
            await self.close(code=4403)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self._track_presence(joined=True)

    async def disconnect(self, close_code):
        # Leave room group
        await self._track_presence(joined=False)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            payload = json.loads(text_data or '{}')
        except json.JSONDecodeError:
            return

        action = payload.get('action')
        user = self.scope.get('resolved_user')
        if not user or not getattr(user, 'is_authenticated', False):
            return

        if action == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_event',
                    'payload': {
                        'action': 'typing',
                        'payload': {
                            'userId': user.id,
                            'userName': user.name or user.email,
                            'isTyping': bool(payload.get('isTyping', False)),
                        }
                    }
                }
            )

    async def chat_message(self, event):
        payload = event['payload']
        await self.send(text_data=json.dumps({
            'action': 'new_message',
            'payload': payload
        }))

    async def chat_event(self, event):
        await self.send(text_data=json.dumps({
            'action': event['payload'].get('action'),
            'payload': event['payload'].get('payload')
        }))

    async def _track_presence(self, *, joined):
        user = self.scope.get('resolved_user')
        if not user or not getattr(user, 'is_authenticated', False):
            return

        room_state = self.room_presence.setdefault(self.room_id, {})
        active_channels = room_state.setdefault(user.id, set())
        if joined:
            active_channels.add(self.channel_name)
        else:
            active_channels.discard(self.channel_name)
            if not active_channels:
                room_state.pop(user.id, None)
        if not room_state:
            self.room_presence.pop(self.room_id, None)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_event',
                'payload': {
                    'action': 'presence',
                    'payload': {
                        'onlineUserIds': list(room_state.keys()),
                    }
                }
            }
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        resolved_user = await _resolve_user(self.scope)
        self.scope['resolved_user'] = resolved_user

        if not resolved_user or not getattr(resolved_user, 'is_authenticated', False):
            await self.close(code=4401)
            return

        self.notification_group_name = f'notifications_{resolved_user.id}'
        await self.channel_layer.group_add(self.notification_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope.get('resolved_user')
        if user and getattr(user, 'is_authenticated', False):
            await self.channel_layer.group_discard(self.notification_group_name, self.channel_name)

    async def notification_event(self, event):
        await self.send(text_data=json.dumps({
            'action': event['payload'].get('action'),
            'payload': event['payload'].get('payload'),
        }))
