
from requests import Response
from rest_framework.decorators import action
from rest_framework.utils import timezone

from members.models import Member
from rest_framework import viewsets, permissions
from mutualApp.models import Session
from .serializers import MemberSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from operationApp.models import ObligatoryContribution
from mutualApp.models import Session
from .models import Member
from .serializers import MemberSerializer


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = MemberSerializer

    @action(detail=True, methods=['get'])
    def debt(self, request, pk=None):
        """
        Endpoint pour obtenir le montant total que doit un membre spécifique.
        """
        member = self.get_object()
        total_debt = member.calculate_debt()
        return Response({"total_debt": total_debt})

    # Actions personnalisées pour accéder directement aux champs spécifiques (si besoin)

    @action(detail=True, methods=['get'])
    def open_help(self, request, pk=None):
        """
        Endpoint pour vérifier si une aide est ouverte pour le membre.
        """
        member = self.get_object()
        open_help = member.has_open_help()
        return Response({"has_open_help": open_help})

    @action(detail=True, methods=['get'])
    def epargnes(self, request, pk=None):
        """
        Endpoint pour obtenir le montant total de l'épargne du membre.
        """
        member = self.get_object()
        total_savings = member.calculate_savings()
        return Response({"total_savings": total_savings})


class UnpaidObligatoryContributionMembersViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        """
        Retourne la liste des membres qui n'ont pas encore payé leur contribution obligatoire
        pour la session active la plus récente.
        """
        # Trouver la session active la plus récente
        session = Session.objects.filter(active=True).order_by('-create_at').first()
        if not session:
            return Response({"error": "Aucune session active trouvée."}, status=404)

        # Obtenir les membres sans contribution obligatoire pour cette session
        unpaid_members = Member.objects.exclude(
            obligatory_contribution__session=session,
            obligatory_contribution__contributed=True
        ).distinct()

        serializer = MemberSerializer(unpaid_members, many=True)
        return Response(serializer.data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from django.contrib.auth.hashers import make_password
from members.models import Member
from administrators.models import Administrator
from mutualApp.models import Session


class RegisterUserView(APIView):
    def post(self, request):
        # Récupérer les données de la requête
        data = request.data
        name = data.get("name")
        first_name = data.get("first_name")
        sex = data.get("sex", "")
        user_type = data.get("type", "member")
        address = data.get("address", "")
        tel = data.get("tel", "")
        email = data.get("email")
        password = data.get("password")

        # Créer l'utilisateur avec les informations de base
        user = User(
            first_name=first_name,
            name=name,
            email=email,
            password=make_password(password),  # Hash du mot de passe
            sex=sex,
            tel=tel,
            address=address,
            type=user_type,
            create_at=timezone.datetime.now()

        )
        user.save()

        # Vérifier le type d'utilisateur et créer l'objet associé
        if user_type == "administrator":
            # Création d'un administrateur
            admin = Administrator.objects.create(
                user_id=user,
                username=name,
                root=1  # Exemple de configuration pour le champ `root`
            )
            response_data = {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "first_name": user.first_name,
                    "email": user.email,
                    "tel": tel,
                    "address": address,
                    "type": "administrator",
                },
                "administrator": {
                    "id": admin.id,
                    "username": admin.username,
                    "root": admin.root,
                    "user_id": admin.user_id.id
                }
            }

        elif user_type == "member":
            # Assigner un administrateur par défaut (id = 1) pour les membres simples
            default_admin_id = 1
            member = Member.objects.create(
                user_id=user,
                username=name,
                social_crown=0,
                administrator_id=Administrator.objects.get(id=default_admin_id)
            )

            response_data = {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "first_name": user.first_name,
                    "email": user.email,
                    "tel": tel,
                    "address": address,
                    "type": "member",
                },
                "member": {
                    "id": member.id,
                    "username": member.username,
                    "active": member.active,
                    "social_crown": member.social_crown,
                    "inscription": member.inscription,
                    "user_id": member.user_id.id,
                    "administrator_id": member.administrator_id.id
                }
            }

        else:
            return Response({"error": "Type d'utilisateur non valide"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status.HTTP_201_CREATED)


