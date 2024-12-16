from administrators.models import Administrator
from rest_framework import viewsets, permissions
from .serializers import AdministratorSerializer
from django_filters.rest_framework import DjangoFilterBackend

class AdministratorViewSet(viewsets.ModelViewSet):
    queryset = Administrator.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = AdministratorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par tout