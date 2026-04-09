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

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # We handle incoming messages via the standard REST API
        # Only used if frontend tries to send via WS natively
        pass

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
