from django.contrib.auth.models import User  # ou ton modèle User personnalisé
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import DeviceToken
from members.models import Member
from users.models import User

@api_view(['POST'])
def register_token(request):
    try:
        token = request.data.get('token')
        user_id = request.data.get('user_id')
        print("le token est :",token)
        print("l'user a pour ID:",user_id)
        if not token or not user_id:
            return Response({"error": "token et user_id requis"}, status=400)

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
