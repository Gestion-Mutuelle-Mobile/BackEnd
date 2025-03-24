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
class PersonalContributionViewSet(viewsets.ModelViewSet):
    queryset = PersonalContribution.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PersonalContributionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par user_id


from rest_framework.decorators import action
from rest_framework.response import Response

class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ContributionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

    def get_queryset(self):
        """
        Redéfinir le queryset pour inclure toutes les contributions
        (ObligatoryContribution et PersonalContribution).
        """
        return Contribution.objects.all()

    @action(detail=False, methods=['get'])
    def obligatory(self, request):
        """
        Endpoint pour retourner les contributions obligatoires et personnelles combinées.
        """
        obligatory_contributions = ObligatoryContribution.objects.all()
        personal_contributions = PersonalContribution.objects.all()

        # Combine les deux ensembles
        all_contributions = list(obligatory_contributions) + list(personal_contributions)

        # Sérialisation des contributions combinées
        serializer = self.get_serializer(all_contributions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def personal(self, request):
        """
        Endpoint pour retourner uniquement les contributions personnelles.
        """
        personal_contributions = PersonalContribution.objects.all()
        serializer = self.get_serializer(personal_contributions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def all_contributions(self, request):
        """
        Endpoint pour retourner les contributions obligatoires et personnelles combinées.
        """
        obligatory_contributions = ObligatoryContribution.objects.all()
        personal_contributions = PersonalContribution.objects.all()

        # Combine les deux ensembles
        all_contributions = list(obligatory_contributions) + list(personal_contributions)

        # Sérialisation des contributions combinées
        serializer = self.get_serializer(all_contributions, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def all_contributions_member(self, request):
        """
        Endpoint pour retourner les contributions obligatoires et personnelles combinées.
        """
        member_id = request.query_params.get('member_id')
        
        obligatory_contributions = ObligatoryContribution.objects.filter(member_id=member_id)
        personal_contributions = PersonalContribution.objects.filter(member_id=member_id)

        # Combine les deux ensembles
        all_contributions = list(obligatory_contributions) + list(personal_contributions)

        # Sérialisation des contributions combinées
        serializer = self.get_serializer(all_contributions, many=True)
        return Response(serializer.data)



class HelpViewSet(viewsets.ModelViewSet):
    queryset = Help.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = HelpSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par user_id

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par user_id

class BorrowingFilterSet(FilterSet):
    class Meta:
        model = Borrowing  # Remplacez par le nom de votre modèle
        # OU
        fields = '__all__' # Incluez uniquement les champs désirés
        # Ajout des overrides pour JSONField
        filter_overrides = {
            JSONField: {
                'filter_class': CharFilter,  # Permet de filtrer comme une chaîne de caractères
            },
        }


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = BorrowingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BorrowingFilterSet

class EpargneViewSet(viewsets.ModelViewSet):
    queryset = Epargne.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EpargneSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par tout


class HelpTypeViewSet(viewsets.ModelViewSet):
    queryset = HelpType.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = HelpTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par tout
class RefundViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RefundSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par tout

    def perform_create(self, serializer):
        refund = serializer.save()
        return Response({'message': 'Remboursement enregistré et distribué aux épargnes.'}, status=status.HTTP_201_CREATED)
    
