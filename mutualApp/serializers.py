from rest_framework import serializers
from mutualApp.models import Exercise
from .models import *


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'



class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

# Sérialiseur pour FondSocial
class FondSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = FondSocial
        fields = '__all__'


# Sérialiseur pour Tresorerie
class TresorerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tresorerie
        fields = '__all__'