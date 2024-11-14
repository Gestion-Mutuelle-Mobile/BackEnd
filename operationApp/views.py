from rest_framework.views import APIView

from .serializers import *
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import *

class PersonalContributionViewSet(viewsets.ModelViewSet):
    queryset = PersonalContribution.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PersonalContributionSerializer




class HelpViewSet(viewsets.ModelViewSet):
    queryset = Help.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = HelpSerializer

    @action(detail=True, methods=['get'])
    def collected_amount(self, request, pk=None):
        """
        Endpoint pour obtenir le montant total collecté pour une aide spécifique.
        """
        help_instance = self.get_object()
        collected_amount = help_instance.calculate_help_amount()
        return Response({"collected_amount": collected_amount})
from rest_framework import status


class CloseHelpView(APIView):
    def patch(self, request, pk):
        """
        Ferme une aide en mettant son champ 'state' à False.
        """
        try:
            help_instance = Help.objects.get(pk=pk)
        except Help.DoesNotExist:
            return Response({"error": "Aide non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        # Fermer l'aide en mettant `state` à False
        help_instance.state = False
        help_instance.save()
        return Response({"message": "L'aide a été fermée avec succès."}, status=status.HTTP_200_OK)


class Obligatory_ContributionViewSet(viewsets.ModelViewSet):
    queryset = ObligatoryContribution.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = Obligatory_ContributionSerializer

class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = BorrowingSerializer

class EpargneViewSet(viewsets.ModelViewSet):
    queryset = Epargne.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EpargneSerializer

class RefundViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RefundSerializer

    def perform_create(self, serializer):
        refund = serializer.save()
        return Response({'message': 'Remboursement enregistré et distribué aux épargnes.'}, status=status.HTTP_201_CREATED)