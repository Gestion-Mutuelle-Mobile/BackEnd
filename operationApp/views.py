
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
