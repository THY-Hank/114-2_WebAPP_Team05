import json
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CustomUser
from .jwt_utils import generate_access_token
from .captcha import is_valid_recaptcha

import base64
import os
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
except ImportError:  # pragma: no cover - local fallback when dependency is missing
    AES = None

    def unpad(value, block_size):
        return value

AES_KEY = os.environ.get('AES_KEY', 'team05_secret_key_12345678901234').encode('utf-8')
AES_IV = os.environ.get('AES_IV', 'team05_shared_iv').encode('utf-8')

def decrypt_password(encrypted_b64):
    if AES is None:
        return encrypted_b64
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
        recaptcha_token = data.get('recaptchaToken', '')
        
        # 验证 reCAPTCHA（v3 分数阈值 0.5）
        if recaptcha_token:
            is_valid, error_msg = is_valid_recaptcha(recaptcha_token, min_score=0.5)
            if not is_valid:
                return JsonResponse({'error': f'CAPTCHA 验证失败: {error_msg}'}, status=400)
        
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
        recaptcha_token = data.get('recaptchaToken', '')
        
        # 验证 reCAPTCHA（v3 分数阈值 0.5）
        if recaptcha_token:
            is_valid, error_msg = is_valid_recaptcha(recaptcha_token, min_score=0.5)
            if not is_valid:
                return JsonResponse({'error': f'CAPTCHA 验证失败: {error_msg}'}, status=400)
        
        password = decrypt_password(encrypted_password) if encrypted_password else None
        if not password:
            return JsonResponse({'error': 'Invalid encrypted password format.'}, status=400)
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            return JsonResponse({
                'message': 'Login successful!',
                'accessToken': generate_access_token(user),
                'user': {'id': user.id, 'email': user.email, 'name': user.name}
            })
        else:
            return JsonResponse({'error': 'Invalid credentials.'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST", "GET"])
def logout_view(request):
    return JsonResponse({'message': 'Logout successful!'})
