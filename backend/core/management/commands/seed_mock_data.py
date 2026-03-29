from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ChatMessage, ChatRoom, CodeFile, FileComment, Project
from user.models import CustomUser


MOCK_USERS = [
    {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "password": "password",
        "projects": [
            {"id": 1, "name": "Project Alpha"},
            {"id": 2, "name": "Project Beta"},
        ],
    },
    {
        "id": 2,
        "name": "Bob",
        "email": "bob@example.com",
        "password": "password",
        "projects": [{"id": 3, "name": "Project Gamma"}],
    },
]

MOCK_FILES = [
    {
        "id": 1,
        "projectId": 1,
        "name": "main.js",
        "content": 'console.log("Hello, World!");',
        "comments": [
            {"id": 1, "author": "Alice", "text": "This looks good."},
            {
                "id": 2,
                "author": "Bob",
                "text": "Could you add a comment explaining this line?",
            },
        ],
    },
    {
        "id": 2,
        "projectId": 1,
        "name": "index.html",
        "content": "<h1>Hello, World!</h1>",
        "comments": [],
    },
    {
        "id": 3,
        "projectId": 1,
        "name": "test.c",
        "content": "void main(){}",
        "comments": [],
    },
]

MOCK_CHAT_ROOMS = [
    {
        "id": 1,
        "name": "Project Alpha",
        "messages": [
            {"id": 1, "author": "Alice", "text": "Hey everyone!"},
            {"id": 2, "author": "Bob", "text": "Hi Alice!"},
        ],
    },
    {
        "id": 2,
        "name": "Private - Charlie",
        "messages": [],
    },
]


class Command(BaseCommand):
    help = "Seed the teammate backend schema with the mock data from frontend/src/stores/main.ts."

    @transaction.atomic
    def handle(self, *args, **options):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        FileComment.objects.all().delete()
        CodeFile.objects.all().delete()
        Project.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()

        users_by_name = {}
        projects_by_id = {}

        for user_data in MOCK_USERS:
            user = CustomUser(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                is_active=True,
            )
            user.set_password(user_data["password"])
            user.save()
            users_by_name[user_data["name"]] = user

            for project_data in user_data["projects"]:
                project = projects_by_id.get(project_data["id"])
                if project is None:
                    project = Project.objects.create(
                        id=project_data["id"],
                        name=project_data["name"],
                        owner=user,
                    )
                    projects_by_id[project_data["id"]] = project
                project.members.add(user)

        for file_data in MOCK_FILES:
            project = projects_by_id[file_data["projectId"]]
            code_file = CodeFile.objects.create(
                id=file_data["id"],
                project=project,
                name=file_data["name"],
                content=file_data["content"],
            )

            for comment_data in file_data["comments"]:
                FileComment.objects.create(
                    id=comment_data["id"],
                    file=code_file,
                    author=users_by_name[comment_data["author"]],
                    text=comment_data["text"],
                )

        for room_data in MOCK_CHAT_ROOMS:
            room = ChatRoom.objects.create(id=room_data["id"], name=room_data["name"])
            room.members.add(*CustomUser.objects.all())
            for message_data in room_data["messages"]:
                snippet = message_data.get("codeSnippet", {})
                ChatMessage.objects.create(
                    id=message_data["id"],
                    room=room,
                    author=users_by_name[message_data["author"]],
                    text=message_data.get("text"),
                    code_snippet_file=snippet.get("fileName"),
                    code_snippet_line=snippet.get("line"),
                )

        self.stdout.write(self.style.SUCCESS("Mock data loaded into teammate backend schema successfully."))
