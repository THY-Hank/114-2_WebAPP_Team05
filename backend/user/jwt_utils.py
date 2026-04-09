import os
from datetime import datetime, timedelta, timezone

import jwt

from .models import CustomUser


JWT_SECRET = os.environ.get('JWT_SECRET', os.environ.get('SECRET_KEY', 'jwt-fallback-secret'))
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_MINUTES = int(os.environ.get('JWT_ACCESS_MINUTES', '60'))


def generate_access_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user.id),
        'email': user.email,
        'iat': now,
        'exp': now + timedelta(minutes=JWT_ACCESS_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_access_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_user_from_token(token):
    payload = verify_access_token(token)
    if not payload:
        return None

    user_id = payload.get('sub')
    if not user_id:
        return None

    try:
        return CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return None