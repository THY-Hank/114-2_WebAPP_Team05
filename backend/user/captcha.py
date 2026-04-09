import requests
import os
import json
import hmac
import hashlib
from django.http import JsonResponse

RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '')
RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
DEBUG_MODE = os.environ.get('DEBUG', 'True').lower() == 'true'

def verify_demo_captcha(token: str) -> dict:
    """
    本地演示 CAPTCHA 验证（用于开发环境）
    模拟 Google reCAPTCHA v3 的响应格式
    
    Args:
        token: 客户端提供的演示令牌
    
    Returns:
        字典包含 {success: bool, score: float, action: str, error: str or None}
    """
    # 演示模式：接受任何非空令牌，并给予 0.8 的分数
    if not token:
        return {
            'success': False,
            'score': 0.0,
            'action': 'unknown',
            'error': None
        }
    
    return {
        'success': True,
        'score': 0.8,  # 演示分数（真实用户范围）
        'action': 'login',
        'error': None
    }

def verify_recaptcha(token: str) -> dict:
    """
    验证 CAPTCHA 令牌（自动选择本地演示或 Google reCAPTCHA）
    
    Args:
        token: 客户端提供的 CAPTCHA 令牌
    
    Returns:
        字典包含 {success: bool, score: float, action: str, error: str or None}
    """
    # 开发环境：使用本地演示
    if DEBUG_MODE or not RECAPTCHA_SECRET_KEY:
        return verify_demo_captcha(token)
    
    # 生产环境：使用 Google reCAPTCHA v3
    try:
        response = requests.post(
            RECAPTCHA_VERIFY_URL,
            data={
                'secret': RECAPTCHA_SECRET_KEY,
                'response': token
            },
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            'success': result.get('success', False),
            'score': result.get('score', 0.0),
            'action': result.get('action', ''),
            'error': None
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'score': 0.0,
            'action': '',
            'error': f'CAPTCHA 验证失败: {str(e)}'
        }
    except ValueError:
        return {
            'success': False,
            'score': 0.0,
            'action': '',
            'error': 'CAPTCHA 响应无效'
        }

def is_valid_recaptcha(token: str, min_score: float = 0.5) -> tuple[bool, str]:
    """
    检查 CAPTCHA 验证是否通过（判断分数）
    
    Args:
        token: 客户端提供的 CAPTCHA 令牌
        min_score: 最低接受分数（0.0-1.0）
    
    Returns:
        tuple: (是否通过, 错误消息)
    """
    result = verify_recaptcha(token)
    
    if result['error']:
        return False, result['error']
    
    if not result['success']:
        return False, '验证失败'
    
    if result['score'] < min_score:
        return False, f'检测到可疑行为 (分数: {result["score"]:.2f})'
    
    return True, ''

def get_captcha_status() -> dict:
    """
    获取当前 CAPTCHA 配置状态
    用于前端了解使用的是哪种 CAPTCHA
    """
    if DEBUG_MODE or not RECAPTCHA_SECRET_KEY:
        return {
            'mode': 'demo',
            'enabled': True,
            'type': 'local-demo',
            'message': '本地演示模式（开发环境）'
        }
    else:
        return {
            'mode': 'production',
            'enabled': True,
            'type': 'google-recaptcha-v3',
            'message': 'Google reCAPTCHA v3（生产环境）'
        }
