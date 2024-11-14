from operationApp.models import PersonalContribution
from rest_framework import viewsets, permissions
from operationApp.serializers import  PersonalContributionSerializer
class ContributionViewSet(viewsets.ModelViewSet):
    queryset = PersonalContribution.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PersonalContributionSerializer