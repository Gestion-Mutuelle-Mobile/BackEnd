# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import DeviceToken
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
def register_token(request):
    data = json.loads(request.body)
    token = data.get("token")
    if token:
        DeviceToken.objects.update_or_create(user=request.user, defaults={"token": token})
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)
