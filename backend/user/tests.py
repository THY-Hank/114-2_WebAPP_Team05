from django.test import TestCase, Client
from django.urls import reverse
import json
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from .models import CustomUser

AES_KEY = os.environ.get('AES_KEY', 'team05_secret_key_12345678901234').encode('utf-8')
AES_IV = os.environ.get('AES_IV', 'team05_shared_iv').encode('utf-8')

def encrypt_password(password):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    encrypted_bytes = cipher.encrypt(pad(password.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted_bytes).decode('utf-8')

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        
        self.raw_password = 'strongpassword123'
        self.encrypted_password = encrypt_password(self.raw_password)
        
        self.user_data_api = {
            'email': 'testuser@example.com',
            'password': self.encrypted_password,
            'name': 'Test User'
        }

    def test_register_user(self):
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data_api),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(email='testuser@example.com').exists())
        self.assertEqual(CustomUser.objects.get(email='testuser@example.com').name, 'Test User')

    def test_register_existing_user(self):
        CustomUser.objects.create_user(email=self.user_data_api['email'], password=self.raw_password, name=self.user_data_api['name'])
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data_api),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_login_user(self):
        CustomUser.objects.create_user(email=self.user_data_api['email'], password=self.raw_password, name=self.user_data_api['name'])
        login_data = {
            'email': 'testuser@example.com',
            'password': self.encrypted_password
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Login successful!')
        self.assertTrue(response.client.session.exists(response.client.session.session_key))

    def test_login_invalid_user(self):
        CustomUser.objects.create_user(email=self.user_data_api['email'], password=self.raw_password, name=self.user_data_api['name'])
        login_data = {
            'email': 'testuser@example.com',
            'password': encrypt_password('wrongpassword')
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.json())

    def test_logout_user(self):
        CustomUser.objects.create_user(email=self.user_data_api['email'], password=self.raw_password, name=self.user_data_api['name'])
        login_data = {
            'email': 'testuser@example.com',
            'password': self.encrypted_password
        }
        self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Logout successful!')
