from django.shortcuts import render


# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class VerifyPasswordView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        password = request.data.get("password")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Vérification du mot de passe en utilisant `check_password`
        if check_password(password, user.password):
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failure"}, status=status.HTTP_401_UNAUTHORIZED)
