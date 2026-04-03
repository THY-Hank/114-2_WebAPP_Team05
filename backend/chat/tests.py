from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock, AsyncMock
import json

from user.models import CustomUser
from core.models import Project
from .models import ChatRoom, ChatMessage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(email, name="Test User", password="pass1234"):
    return CustomUser.objects.create_user(email=email, password=password, name=name)


def make_project(name="Test Project", owner=None, members=None):
    project = Project.objects.create(name=name, owner=owner)
    if members:
        project.members.set(members)
    return project


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------

class ChatRoomModelTest(TestCase):
    def setUp(self):
        self.user = make_user("owner@example.com", name="Owner")
        self.project = make_project(owner=self.user, members=[self.user])

    def test_chatroom_str_with_project(self):
        room = ChatRoom.objects.create(name="general", project=self.project)
        self.assertEqual(str(room), f"{self.project.name} - general")

    def test_chatroom_str_without_project(self):
        room = ChatRoom.objects.create(name="standalone")
        self.assertEqual(str(room), "standalone")

    def test_chatroom_members(self):
        room = ChatRoom.objects.create(name="general", project=self.project)
        room.members.set([self.user])
        self.assertIn(self.user, room.members.all())


class ChatMessageModelTest(TestCase):
    def setUp(self):
        self.user = make_user("author@example.com", name="Author")
        self.project = make_project(owner=self.user, members=[self.user])
        self.room = ChatRoom.objects.create(name="general", project=self.project)
        self.room.members.set([self.user])

    def test_message_str(self):
        msg = ChatMessage.objects.create(room=self.room, author=self.user, text="Hello")
        # __str__ uses author.email, not author.name
        self.assertIn("author@example.com", str(msg))
        self.assertIn("general", str(msg))

    def test_message_with_code_snippet(self):
        msg = ChatMessage.objects.create(
            room=self.room,
            author=self.user,
            code_snippet_file="main.py",
            code_snippet_line=10,
            code_snippet_start_line=8,
            code_snippet_end_line=12,
            code_snippet_content="print('hello')"
        )
        self.assertEqual(msg.code_snippet_file, "main.py")
        self.assertEqual(msg.code_snippet_content, "print('hello')")

    def test_message_text_optional(self):
        # text is blank/null; should not raise
        msg = ChatMessage.objects.create(
            room=self.room, author=self.user,
            code_snippet_file="app.py"
        )
        self.assertIsNone(msg.text)


# ---------------------------------------------------------------------------
# View Tests — project_chatrooms_view  (GET / POST)
# ---------------------------------------------------------------------------

class ProjectChatroomsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = make_user("owner@example.com", name="Owner")
        self.other = make_user("other@example.com", name="Other")
        self.outsider = make_user("outsider@example.com", name="Outsider")
        self.project = make_project(owner=self.owner, members=[self.owner, self.other])
        self.url = reverse("api_project_chatrooms", args=[self.project.id])

    def _login(self, user):
        self.client.force_login(user)

    # --- Authentication guard ---

    def test_unauthenticated_get_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_post_returns_401(self):
        response = self.client.post(self.url, data=json.dumps({"name": "x"}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 401)

    # --- Outsider (not a project member) ---

    def test_outsider_get_returns_404(self):
        self._login(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_outsider_post_returns_404(self):
        self._login(self.outsider)
        response = self.client.post(self.url, data=json.dumps({"name": "x"}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 404)

    # --- GET chatrooms ---

    def test_get_chatrooms_empty(self):
        self._login(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_chatrooms_only_own_rooms(self):
        """Owner only sees rooms they are a member of."""
        room_mine = ChatRoom.objects.create(name="mine", project=self.project)
        room_mine.members.set([self.owner])
        room_others = ChatRoom.objects.create(name="others", project=self.project)
        room_others.members.set([self.other])

        self._login(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        names = [r["name"] for r in response.json()]
        self.assertIn("mine", names)
        self.assertNotIn("others", names)

    def test_get_chatroom_includes_messages(self):
        room = ChatRoom.objects.create(name="general", project=self.project)
        room.members.set([self.owner])
        ChatMessage.objects.create(room=room, author=self.owner, text="Hi!")

        self._login(self.owner)
        data = self.client.get(self.url).json()
        self.assertEqual(len(data[0]["messages"]), 1)
        self.assertEqual(data[0]["messages"][0]["text"], "Hi!")

    # --- POST create chatroom ---

    def test_post_missing_name_returns_400(self):
        self._login(self.owner)
        response = self.client.post(self.url, data=json.dumps({}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_post_creates_room_with_all_project_members_when_no_member_ids(self):
        self._login(self.owner)
        response = self.client.post(
            self.url,
            data=json.dumps({"name": "general"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        room = ChatRoom.objects.get(name="general", project=self.project)
        member_ids = set(room.members.values_list("id", flat=True))
        self.assertIn(self.owner.id, member_ids)
        self.assertIn(self.other.id, member_ids)

    def test_post_creates_room_with_explicit_member_ids(self):
        self._login(self.owner)
        response = self.client.post(
            self.url,
            data=json.dumps({"name": "private", "memberIds": [self.owner.id]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        room = ChatRoom.objects.get(name="private", project=self.project)
        self.assertEqual(room.members.count(), 1)

    def test_post_creator_always_added_when_not_in_member_ids(self):
        """Even if creator's ID is missing from memberIds, they are still added."""
        self._login(self.owner)
        response = self.client.post(
            self.url,
            data=json.dumps({"name": "exclusive", "memberIds": [self.other.id]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        room = ChatRoom.objects.get(name="exclusive", project=self.project)
        member_ids = set(room.members.values_list("id", flat=True))
        self.assertIn(self.owner.id, member_ids)

    def test_post_returns_serialized_room(self):
        self._login(self.owner)
        response = self.client.post(
            self.url,
            data=json.dumps({"name": "general"}),
            content_type="application/json"
        )
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "general")
        self.assertEqual(data["projectId"], self.project.id)
        self.assertEqual(data["messages"], [])


# ---------------------------------------------------------------------------
# View Tests — add_chat_message_view  (POST)
# ---------------------------------------------------------------------------

class AddChatMessageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = make_user("owner@example.com", name="Owner")
        self.outsider = make_user("outsider@example.com", name="Outsider")
        self.project = make_project(owner=self.owner, members=[self.owner])
        self.room = ChatRoom.objects.create(name="general", project=self.project)
        self.room.members.set([self.owner])
        self.url = reverse(
            "api_add_chat_message",
            args=[self.project.id, self.room.id]
        )

    def _login(self, user):
        self.client.force_login(user)

    # --- Authentication / authorisation ---

    def test_unauthenticated_returns_401(self):
        response = self.client.post(self.url, data=json.dumps({"text": "hi"}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_non_member_returns_404(self):
        self._login(self.outsider)
        response = self.client.post(self.url, data=json.dumps({"text": "hi"}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 404)

    # --- Validation ---

    def test_empty_body_returns_400(self):
        self._login(self.owner)
        response = self.client.post(self.url, data=json.dumps({}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)

    # --- Successful text message ---

    @patch("chat.views.get_channel_layer")
    def test_post_text_message_returns_201(self, mock_get_layer):
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()  # group_send is a coroutine
        mock_get_layer.return_value = mock_layer

        self._login(self.owner)
        response = self.client.post(
            self.url,
            data=json.dumps({"text": "Hello World"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["text"], "Hello World")
        # author field uses name if set, else email
        self.assertIn(data["author"], ["Owner", "owner@example.com"])
        self.assertIn("id", data)
        self.assertIn("createdAt", data)

    @patch("chat.views.get_channel_layer")
    def test_post_text_message_persisted(self, mock_get_layer):
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_get_layer.return_value = mock_layer

        self._login(self.owner)
        self.client.post(self.url, data=json.dumps({"text": "Persisted"}),
                         content_type="application/json")
        self.assertTrue(ChatMessage.objects.filter(text="Persisted", room=self.room).exists())

    # --- Successful code snippet message ---

    @patch("chat.views.get_channel_layer")
    def test_post_code_snippet_message(self, mock_get_layer):
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_get_layer.return_value = mock_layer

        self._login(self.owner)
        payload = {
            "codeSnippetFile": "app.py",
            "codeSnippetLine": 5,
            "codeSnippetStartLine": 3,
            "codeSnippetEndLine": 7,
            "codeSnippetContent": "def foo(): pass"
        }
        response = self.client.post(self.url, data=json.dumps(payload),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("codeSnippet", data)
        self.assertEqual(data["codeSnippet"]["fileName"], "app.py")
        self.assertEqual(data["codeSnippet"]["content"], "def foo(): pass")

    # --- WebSocket broadcast is called ---

    @patch("chat.views.async_to_sync")
    @patch("chat.views.get_channel_layer")
    def test_websocket_broadcast_called(self, mock_get_layer, mock_async_to_sync):
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_get_layer.return_value = mock_layer
        mock_send = MagicMock()
        mock_async_to_sync.return_value = mock_send

        self._login(self.owner)
        self.client.post(self.url, data=json.dumps({"text": "broadcast test"}),
                         content_type="application/json")

        mock_async_to_sync.assert_called_once()
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[0]
        self.assertEqual(call_kwargs[0], f"chat_{self.room.id}")
        self.assertEqual(call_kwargs[1]["type"], "chat_message")


# ---------------------------------------------------------------------------
# WebSocket Consumer Tests
# ---------------------------------------------------------------------------

from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chat.consumers import ChatConsumer
from chat.routing import websocket_urlpatterns
from channels.routing import URLRouter
from django.test import override_settings


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
class ChatConsumerTest(TestCase):
    """
    Tests for the ChatConsumer WebSocket consumer.
    Uses channels.testing.WebsocketCommunicator for in-process testing.
    """

    async def _make_communicator(self, room_id=1):
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(application, f"/ws/chat/{room_id}/")
        return communicator

    def test_connect_and_disconnect(self):
        async def run():
            comm = await self._make_communicator(room_id=42)
            connected, _ = await comm.connect()
            self.assertTrue(connected)
            await comm.disconnect()
        import asyncio
        asyncio.get_event_loop().run_until_complete(run())

    def test_receive_broadcast_message(self):
        """
        Send a message to the group via the channel layer and verify
        the consumer forwards it through the WebSocket.
        """
        async def run():
            comm = await self._make_communicator(room_id=99)
            connected, _ = await comm.connect()
            self.assertTrue(connected)

            layer = get_channel_layer()
            payload = {"id": 1, "author": "Alice", "text": "Hi", "createdAt": "2026-01-01T00:00:00"}
            await layer.group_send(
                "chat_99",
                {"type": "chat_message", "payload": payload}
            )

            response = await comm.receive_json_from(timeout=3)
            self.assertEqual(response["action"], "new_message")
            self.assertEqual(response["payload"]["text"], "Hi")

            await comm.disconnect()
        import asyncio
        asyncio.get_event_loop().run_until_complete(run())
