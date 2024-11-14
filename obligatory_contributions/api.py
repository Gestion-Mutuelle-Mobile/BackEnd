from operationApp.models import ObligatoryContribution
from rest_framework import viewsets, permissions
from .serializers import Obligatory_ContributionSerializer

class Obligatory_ContributionViewSet(viewsets.ModelViewSet):
    queryset = ObligatoryContribution.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = Obligatory_ContributionSerializer