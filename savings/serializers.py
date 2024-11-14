from rest_framework import serializers
from .models import Epargne

class EpargneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Epargne
        fields = '__all__'

    def get_fond_social_percentage(self, obj):
        return obj.calculate_tresorerie_percentage()