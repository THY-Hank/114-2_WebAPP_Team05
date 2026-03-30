from django.test import TestCase, Client
from django.urls import reverse
import json
from user.models import CustomUser
from .models import Project, CodeFile, FileComment, ChatRoom, ChatMessage

class CoreAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        # 建立測試用帳號並登入
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password123', name='Test User')
        self.client.force_login(self.user)

        # 建立專案與加入成員
        self.project = Project.objects.create(name='Test Project')
        self.project.members.add(self.user)

        # 建立測試用程式碼檔案
        self.code_file = CodeFile.objects.create(project=self.project, name='test.js', content='console.log("hello");')
        
        # 建立測試聊天室
        self.chat_room = ChatRoom.objects.create(name='Test Room', project=self.project)
        self.chat_room.members.add(self.user)

    def test_get_user_me(self):
        response = self.client.get(reverse('api_me'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['name'], 'Test Project')

    def test_unauthenticated_access(self):
        # 測試未登入時的攔截
        self.client.logout()
        response = self.client.get(reverse('api_me'))
        self.assertEqual(response.status_code, 401)

    def test_upload_file(self):
        response = self.client.post(
            reverse('api_project_files', args=[self.project.id]),
            data=json.dumps({'name': 'newfile.py', 'content': 'print("hi")'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CodeFile.objects.filter(name='newfile.py').exists())

    def test_get_project_files(self):
        response = self.client.get(reverse('api_project_files', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test.js')

    def test_add_file_comment(self):
        response = self.client.post(
            reverse('api_add_file_comment', args=[self.code_file.id]),
            data=json.dumps({'text': 'Great code!'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FileComment.objects.count(), 1)
        self.assertEqual(FileComment.objects.first().text, 'Great code!')

    def test_create_chatroom(self):
        response = self.client.post(
            reverse('api_project_chatrooms', args=[self.project.id]),
            data=json.dumps({'name': 'New Room'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ChatRoom.objects.filter(name='New Room').exists())

    def test_get_chatrooms(self):
        response = self.client.get(reverse('api_project_chatrooms', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Room')

    def test_add_chat_message(self):
        response = self.client.post(
            reverse('api_add_chat_message', args=[self.project.id, self.chat_room.id]),
            data=json.dumps({'text': 'Hello world!'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ChatMessage.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.first().text, 'Hello world!')

    def test_add_chat_snippet(self):
        response = self.client.post(
            reverse('api_add_chat_message', args=[self.project.id, self.chat_room.id]),
            data=json.dumps({'codeSnippetFile': 'test.js', 'codeSnippetLine': 5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ChatMessage.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.first().code_snippet_file, 'test.js')
        self.assertEqual(ChatMessage.objects.first().code_snippet_line, 5)

    def test_create_project(self):
        response = self.client.post(
            reverse('api_projects'),
            data=json.dumps({'name': 'Another Project'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.filter(name='Another Project').count(), 1)

    def test_add_project_member(self):
        from .models import ProjectInvitation
        new_user = CustomUser.objects.create_user(email='partner@example.com', password='password123', name='Partner')
        response = self.client.post(
            reverse('api_project_members', args=[self.project.id]),
            data=json.dumps({'email': 'partner@example.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.project.members.count(), 1)  # the owner is still the only member
        self.assertEqual(ProjectInvitation.objects.count(), 1)

    def test_invitation_flow_accept(self):
        from .models import ProjectInvitation
        partner = CustomUser.objects.create_user(email='partner2@example.com', password='pw')
        ProjectInvitation.objects.create(project=self.project, inviter=self.user, invitee=partner)
        
        self.client.force_login(partner)
        
        # list invites
        resp2 = self.client.get(reverse('api_invitation_list'))
        inv_data = resp2.json()
        self.assertEqual(len(inv_data), 1)
        inv_id = inv_data[0]['id']
        
        # respond
        resp3 = self.client.post(
            reverse('api_invitation_respond', args=[inv_id]),
            json.dumps({'action': 'accept'}),
            content_type='application/json'
        )
        self.assertEqual(resp3.status_code, 200)
        self.assertTrue(self.project.members.filter(id=partner.id).exists())

    def test_invitation_flow_decline(self):
        from .models import ProjectInvitation
        partner = CustomUser.objects.create_user(email='partner3@example.com', password='pw')
        inv = ProjectInvitation.objects.create(project=self.project, inviter=self.user, invitee=partner)
        
        self.client.force_login(partner)
        resp = self.client.post(
            reverse('api_invitation_respond', args=[inv.id]),
            json.dumps({'action': 'decline'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.project.members.filter(id=partner.id).exists())

    def test_delete_project_as_owner(self):
        self.client.force_login(self.user)
        # Create a project directly where test user is the owner
        response = self.client.post(reverse('api_projects'), json.dumps({'name': 'To Delete'}), content_type='application/json')
        proj_id = response.json()['id']
        
        delete_response = self.client.delete(reverse('api_project_detail', args=[proj_id]))
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(Project.objects.filter(id=proj_id).count(), 0)

    def test_delete_project_as_non_owner(self):
        # Create user2 and user3
        user2 = CustomUser.objects.create_user(email='owner@example.com', password='pw')
        self.client.force_login(user2)
        response = self.client.post(reverse('api_projects'), json.dumps({'name': 'Owner Project'}), content_type='application/json')
        proj_id = response.json()['id']
        proj = Project.objects.get(id=proj_id)
        
        # Test User (who is not owner) tries to delete
        self.client.force_login(self.user)
        delete_response = self.client.delete(reverse('api_project_detail', args=[proj_id]))
        self.assertEqual(delete_response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=proj_id).exists())

    def test_delete_file_as_member(self):
        self.client.force_login(self.user)
        # Upload a file
        response = self.client.post(reverse('api_project_files', args=[self.project.id]), json.dumps({'name': 'file1.txt', 'content': '...'}), content_type='application/json')
        file_id = response.json()['id']
        
        delete_response = self.client.delete(reverse('api_file_detail', args=[file_id]))
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(CodeFile.objects.filter(id=file_id).count(), 0)
