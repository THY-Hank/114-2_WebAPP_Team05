import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CustomUser

import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

AES_KEY = os.environ.get('AES_KEY', 'team05_secret_key_12345678901234').encode('utf-8')
AES_IV = os.environ.get('AES_IV', 'team05_shared_iv').encode('utf-8')

def decrypt_password(encrypted_b64):
    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        decrypted_padded = cipher.decrypt(encrypted_bytes)
        decrypted = unpad(decrypted_padded, AES.block_size)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        encrypted_password = data.get('password')
        name = data.get('name', '')
        
        password = decrypt_password(encrypted_password) if encrypted_password else None
        
        if not email or not password:
            return JsonResponse({'error': 'Email and valid encrypted password are required.'}, status=400)
            
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User with this email already exists.'}, status=400)
            
        user = CustomUser.objects.create_user(email=email, password=password, name=name)
        return JsonResponse({'message': 'User registered successfully!', 'user': {'email': user.email, 'name': user.name}}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        encrypted_password = data.get('password')
        
        password = decrypt_password(encrypted_password) if encrypted_password else None
        if not password:
            return JsonResponse({'error': 'Invalid encrypted password format.'}, status=400)
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'message': 'Login successful!',
                'user': {'email': user.email, 'name': user.name}
            })
        else:
            return JsonResponse({'error': 'Invalid credentials.'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST", "GET"])
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful!'})
