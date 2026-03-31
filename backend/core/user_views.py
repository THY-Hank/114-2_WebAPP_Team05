from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def login_check(func):
    """Simple decorator or wrapper to ensure JSON responses for unauthenticated users."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        return func(request, *args, **kwargs)
    return wrapper

@csrf_exempt
@require_http_methods(["GET"])
@login_check
def me_view(request):
    """Returns current user profile and their projects."""
    user = request.user
    projects = []
    for p in user.projects.all():
        projects.append({
            'id': p.id,
            'name': p.name,
            'owner_id': p.owner_id,
            'members': [{'id': m.id, 'name': m.name, 'email': m.email} for m in p.members.all()]
        })
    return JsonResponse({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'projects': projects
    }, status=200)
