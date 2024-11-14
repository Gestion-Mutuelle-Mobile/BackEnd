from operationApp.models import Epargne
from rest_framework import viewsets, permissions
from .serializers import EpargneSerializer

class EpargneViewSet(viewsets.ModelViewSet):
    queryset = Epargne.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EpargneSerializer