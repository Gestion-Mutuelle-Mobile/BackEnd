from rest_framework import serializers
from mutualApp.models import Session
from operationApp.models import ObligatoryContribution
from operationApp.models import Help
from operationApp.models import Epargne

class FondSocialSerializer(serializers.Serializer):
    exercice_id = serializers.IntegerField()
    fonds_social = serializers.IntegerField()

class TresorerieSerializer(serializers.Serializer):
    exercice_id = serializers.IntegerField()
    tresorerie = serializers.IntegerField()