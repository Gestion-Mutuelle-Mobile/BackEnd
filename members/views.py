from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters import FilterSet
from django.db.models import JSONField
from django_filters.filters import CharFilter
from .serializers import *
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet,CharFilter
from .models import DeviceToken, Notification
from .serializers import NotificationSerializer
from users.models import User  # Ton modèle User personnalisé (à conserver si tu l’as redéfini)
# from django.contrib.auth.models import User  # à éviter si User personnalisé
from rest_framework import generics
# API GET: Toutes les notifications (admin uniquement)
class AllNotificationsView(generics.ListAPIView):
    queryset = Notification.objects.all().order_by('-sent_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.AllowAny]  # Change si besoin
    filter_backends = [DjangoFilterBackend]
    filterset_fields =  '__all__'

# API POST: Enregistrer le token FCM d’un utilisateur
@api_view(['POST'])
def register_token(request):
    try:
        token = request.data.get('token')
        user_id = request.data.get('user_id')

        print("Token reçu :", token)
        print("ID utilisateur :", user_id)

        if not token or not user_id:
            return Response({"error": "token et user_id sont requis"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé"}, status=404)

        DeviceToken.objects.update_or_create(user=user, defaults={'token': token})
        return Response({"status": "ok"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def send_notification(request):
    user_id = request.data.get('user_id')
    title = "Rappel de contribution"
    body = f"Salut {user_id.username}, vous n'avez pas encore payé votre contribution de la session."
    # Crée une notification
    Notification.objects.create(user=user_id, title=title, body=body)
    return Response({'message': 'Notification envoyée.'})

@api_view(['POST'])
def send_notification_All(request):

    try:
        members = Member.objects.filter(has_contribued_for_session=False)
        for member in members:
            title = "Rappel de contribution"
            body = f"Salut {member.username}, vous n'avez pas encore payé votre contribution de la session."

            Notification.objects.create(user=member.user, title=title, body=body)

        return Response({'message': f'Notifications envoyées à {members.count()} membres.'})

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
