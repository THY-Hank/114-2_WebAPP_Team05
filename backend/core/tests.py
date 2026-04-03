from django.test import TestCase, Client
from django.urls import reverse
import json
from user.models import CustomUser
from .models import Project, CodeFile, FileComment
from chat.models import ChatRoom, ChatMessage

class CoreAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        # 建立測試用帳號並登入
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password123', name='Test User')
        self.client.force_login(self.user)

        # 建立專案與加入成員
        self.project = Project.objects.create(name='Test Project', owner=self.user)
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

    # =============== Line-Level Comments Tests ===============
    def test_add_line_comment(self):
        """Test creating a line-level comment"""
        response = self.client.post(
            reverse('api_line_comments', args=[self.code_file.id]),
            data=json.dumps({
                'text': 'This line needs refactoring',
                'startLine': 1,
                'endLine': 1
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        comment = FileComment.objects.get(text='This line needs refactoring')
        self.assertEqual(comment.comment_type, 'line')
        self.assertEqual(comment.start_line, 1)
        self.assertEqual(comment.end_line, 1)
        
        data = response.json()
        self.assertEqual(data['startLine'], 1)
        self.assertEqual(data['endLine'], 1)

    def test_add_multiline_comment(self):
        """Test creating a comment spanning multiple lines"""
        response = self.client.post(
            reverse('api_line_comments', args=[self.code_file.id]),
            data=json.dumps({
                'text': 'This block can be optimized',
                'startLine': 5,
                'endLine': 12
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        comment = FileComment.objects.get(text='This block can be optimized')
        self.assertEqual(comment.start_line, 5)
        self.assertEqual(comment.end_line, 12)

    def test_get_line_comments(self):
        """Test retrieving all line-level comments for a file"""
        # Add multiple comments
        FileComment.objects.create(
            file=self.code_file,
            author=self.user,
            text='Comment on line 1',
            comment_type='line',
            start_line=1,
            end_line=1
        )
        FileComment.objects.create(
            file=self.code_file,
            author=self.user,
            text='Comment on lines 3-5',
            comment_type='line',
            start_line=3,
            end_line=5
        )
        # Add a file-level comment (should not be in response)
        FileComment.objects.create(
            file=self.code_file,
            author=self.user,
            text='File-level comment',
            comment_type='file'
        )
        
        response = self.client.get(reverse('api_line_comments', args=[self.code_file.id]))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 2)  # Only line comments, not file comments
        
        line_ranges = [(c['startLine'], c['endLine']) for c in data]
        self.assertIn((1, 1), line_ranges)
        self.assertIn((3, 5), line_ranges)

    def test_add_line_comment_missing_fields(self):
        """Test validation when fields are missing"""
        response = self.client.post(
            reverse('api_line_comments', args=[self.code_file.id]),
            data=json.dumps({
                'text': 'No line info'
                # Missing startLine and endLine
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_add_line_comment_unauthorized(self):
        """Test that only project members can add line comments"""
        other_user = CustomUser.objects.create_user(
            email='other@example.com',
            password='password123',
            name='Other User'
        )
        self.client.force_login(other_user)
        
        response = self.client.post(
            reverse('api_line_comments', args=[self.code_file.id]),
            data=json.dumps({
                'text': 'Unauthorized comment',
                'startLine': 1,
                'endLine': 1
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    # =============== Line-Level Code Share Tests ===============
    def test_add_line_code_snippet_message(self):
        """Test sharing multiple lines of code to chat"""
        response = self.client.post(
            reverse('api_add_chat_message', args=[self.project.id, self.chat_room.id]),
            data=json.dumps({
                'codeSnippetFile': 'test.js',
                'codeSnippetStartLine': 3,
                'codeSnippetEndLine': 7,
                'codeSnippetContent': 'function test() {\n  return true;\n}\n...'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        msg = ChatMessage.objects.first()
        self.assertEqual(msg.code_snippet_file, 'test.js')
        self.assertEqual(msg.code_snippet_start_line, 3)
        self.assertEqual(msg.code_snippet_end_line, 7)
        self.assertTrue('function test' in msg.code_snippet_content)
        
        data = response.json()
        self.assertEqual(data['codeSnippet']['startLine'], 3)
        self.assertEqual(data['codeSnippet']['endLine'], 7)

    def test_add_single_line_code_snippet(self):
        """Test sharing a single line of code"""
        response = self.client.post(
            reverse('api_add_chat_message', args=[self.project.id, self.chat_room.id]),
            data=json.dumps({
                'codeSnippetFile': 'test.js',
                'codeSnippetStartLine': 5,
                'codeSnippetEndLine': 5,
                'codeSnippetContent': 'console.log("hello");'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        msg = ChatMessage.objects.first()
        self.assertEqual(msg.code_snippet_start_line, 5)
        self.assertEqual(msg.code_snippet_end_line, 5)

    def test_previous_code_snippet_format_still_works(self):
        """Test backward compatibility with single-line code snippet format"""
        response = self.client.post(
            reverse('api_add_chat_message', args=[self.project.id, self.chat_room.id]),
            data=json.dumps({
                'codeSnippetFile': 'test.js',
                'codeSnippetLine': 1  # Old format with single line
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        msg = ChatMessage.objects.first()
        self.assertEqual(msg.code_snippet_file, 'test.js')
        self.assertEqual(msg.code_snippet_line, 1)  # Old field still works

    def test_line_code_snippet_with_text_message(self):
        """Test sharing code snippet with accompanying text message"""
        response = self.client.post(
            reverse('api_add_chat_message', args=[self.project.id, self.chat_room.id]),
            data=json.dumps({
                'text': 'Check out this implementation:',
                'codeSnippetFile': 'test.js',
                'codeSnippetStartLine': 2,
                'codeSnippetEndLine': 4,
                'codeSnippetContent': 'const x = 42;\nreturn x;'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        msg = ChatMessage.objects.first()
        self.assertEqual(msg.text, 'Check out this implementation:')
        self.assertEqual(msg.code_snippet_start_line, 2)
        self.assertEqual(msg.code_snippet_end_line, 4)

    def test_file_comment_type_distinction(self):
        """Test that file and line comments are properly distinguished"""
        # Create a file-level comment
        FileComment.objects.create(
            file=self.code_file,
            author=self.user,
            text='Overall file comment',
            comment_type='file'
        )
        # Create line comments
        FileComment.objects.create(
            file=self.code_file,
            author=self.user,
            text='Line 1 comment',
            comment_type='line',
            start_line=1,
            end_line=1
        )
        
        # Get only line comments endpoint
        response = self.client.get(reverse('api_line_comments', args=[self.code_file.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should only return line comments
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['text'], 'Line 1 comment')

    # ==================== ProjectSettings Tests ====================
    
    def test_get_project_settings_owner(self):
        """Test owner can fetch project settings with members list"""
        response = self.client.get(reverse('api_project_settings', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should return project info and members
        self.assertEqual(data['id'], self.project.id)
        self.assertEqual(data['name'], 'Test Project')
        self.assertEqual(data['owner_id'], self.user.id)
        self.assertTrue('members' in data)
        self.assertEqual(len(data['members']), 1)  # Only owner
        self.assertEqual(data['members'][0]['id'], self.user.id)
        self.assertTrue(data['members'][0]['isOwner'])

    def test_get_project_settings_member(self):
        """Test member can fetch project settings"""
        # Add another member to project
        member = CustomUser.objects.create_user(email='member@example.com', password='pw', name='Member')
        self.project.members.add(member)
        
        self.client.force_login(member)
        response = self.client.get(reverse('api_project_settings', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Member can view but should see isOwner=False
        self.assertEqual(len(data['members']), 2)
        member_data = next((m for m in data['members'] if m['id'] == member.id), None)
        self.assertFalse(member_data['isOwner'])

    def test_update_project_name_as_owner(self):
        """Test owner can update project name"""
        response = self.client.put(
            reverse('api_project_settings', args=[self.project.id]),
            data=json.dumps({'name': 'Updated Project Name'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify project name was updated
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project Name')

    def test_update_project_name_as_member(self):
        """Test member cannot update project name"""
        member = CustomUser.objects.create_user(email='member2@example.com', password='pw', name='Member2')
        self.project.members.add(member)
        self.client.force_login(member)
        
        response = self.client.put(
            reverse('api_project_settings', args=[self.project.id]),
            data=json.dumps({'name': 'Hacked Name'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        
        # Verify project name unchanged
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Test Project')

    def test_remove_member_as_owner(self):
        """Test owner can remove members from project"""
        member = CustomUser.objects.create_user(email='member3@example.com', password='pw', name='Member3')
        self.project.members.add(member)
        
        # Add member to a chat room
        self.chat_room.members.add(member)
        
        self.assertEqual(self.project.members.count(), 2)
        self.assertEqual(self.chat_room.members.count(), 2)
        
        # Remove member
        response = self.client.delete(
            reverse('api_project_settings', args=[self.project.id]),
            data=json.dumps({'member_id': member.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify member removed from project
        self.assertEqual(self.project.members.count(), 1)
        self.assertFalse(self.project.members.filter(id=member.id).exists())
        
        # Verify member removed from associated chat rooms
        self.assertEqual(self.chat_room.members.count(), 1)
        self.assertFalse(self.chat_room.members.filter(id=member.id).exists())

    def test_remove_member_cannot_remove_self(self):
        """Test owner cannot remove themselves from project"""
        response = self.client.delete(
            reverse('api_project_settings', args=[self.project.id]),
            data=json.dumps({'member_id': self.user.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.project.members.count(), 1)

    def test_remove_member_as_non_owner(self):
        """Test non-owner cannot remove members"""
        member1 = CustomUser.objects.create_user(email='member4@example.com', password='pw', name='Member4')
        member2 = CustomUser.objects.create_user(email='member5@example.com', password='pw', name='Member5')
        self.project.members.add(member1)
        self.project.members.add(member2)
        
        self.client.force_login(member1)
        
        response = self.client.delete(
            reverse('api_project_settings', args=[self.project.id]),
            data=json.dumps({'member_id': member2.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.project.members.count(), 3)

    def test_remove_non_member_returns_error(self):
        """Test removing a user who is not a member returns error"""
        non_member = CustomUser.objects.create_user(email='nonmember@example.com', password='pw', name='NonMember')
        
        response = self.client.delete(
            reverse('api_project_settings', args=[self.project.id]),
            data=json.dumps({'member_id': non_member.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
