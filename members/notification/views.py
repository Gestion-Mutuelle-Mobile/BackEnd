# notifications/views.py
from django.http import JsonResponse
from .service import notify_non_contributors

def notify_view(request):
    notify_non_contributors()
    return JsonResponse({"status": "Notifications envoyées"})
