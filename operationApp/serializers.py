from rest_framework import serializers
from .models import *

class PersonalContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalContribution
        fields = '__all__'


class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = '__all__'

    def get_collected_amount(self, obj):
        return obj.calculate_help_amount()