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

class Obligatory_ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObligatoryContribution
        fields = '__all__'

class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = '__all__'

class EpargneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Epargne
        fields = '__all__'

    def get_fond_social_percentage(self, obj):
        return obj.calculate_tresorerie_percentage()

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'