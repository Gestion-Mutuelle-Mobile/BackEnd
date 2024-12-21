from members.models import User
from rest_framework import viewsets, permissions
from .serializers import UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django_filters import FilterSet ,CharFilter



class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = '__all__'
        filter_overrides = {
            models.ImageField: {
                'filter_class': CharFilter,  # Utilise CharFilter pour les ImageField
            },
        }
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__' # Autorise le filtrage par user_id
    filterset_class = UserFilter  # Utilise le filtre personnalisé
