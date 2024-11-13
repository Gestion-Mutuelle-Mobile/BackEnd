from requests import Response
from rest_framework.decorators import action

from members.models import Member
from rest_framework import viewsets, permissions
from mutualApp.models import Session
from .serializers import MemberSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from obligatory_contributions.models import Obligatory_Contribution
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
    #permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Retourne la liste des membres qui n'ont pas encore payé leur contribution obligatoire pour toutes les sessions.
        """
        # Obtenir les membres qui n'ont pas encore payé leur contribution pour toutes les sessions
        unpaid_members = Member.objects.filter(
            obligatory_contribution__contributed=0
        ).distinct()

        # Sérialiser les membres
        serializer = MemberSerializer(unpaid_members, many=True)
        return Response(serializer.data)