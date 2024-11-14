from rest_framework import serializers
from mutualApp.models import Session
from obligatory_contributions.models import Obligatory_Contribution
from operationApp.models import Help
from savings.models import Saving

class FondSocialSerializer(serializers.Serializer):
    exercice_id = serializers.IntegerField()
    fonds_social = serializers.IntegerField()

class TresorerieSerializer(serializers.Serializer):
    exercice_id = serializers.IntegerField()
    tresorerie = serializers.IntegerField()