
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import DeviceToken

@api_view(['POST'])
@login_required
def register_token(request):
    token = request.data.get('token')
    if token:
        DeviceToken.objects.update_or_create(user=request.user, defaults={'token': token})
        return Response({"status": "ok"})
    return Response({"status": "error"}, status=400)
