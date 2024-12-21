from rest_framework import serializers

from members.serializers import MemberSerializer
from .models import *

class PersonalContributionSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur

    class Meta:
        model = PersonalContribution
        fields = '__all__'

class ContributionSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure les infos du membre

    class Meta:
        model = Contribution
        fields = '__all__'

    def to_representation(self, instance):
        """
        Ajoute les champs spécifiques selon le type de contribution.
        """
        representation = super().to_representation(instance)

        # Détecter le type de contribution
        if isinstance(instance, ObligatoryContribution):
            representation['type'] = 'Obligatory'
            representation['contributed'] = instance.contributed
            representation['amount'] = instance.amount
        elif isinstance(instance, PersonalContribution):
            representation['type'] = 'Personal'
            representation['date'] = instance.date
            representation['help_id'] = instance.help_id.id if instance.help_id else None
            representation['amount'] = instance.amount

        return representation

class HelpSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur

    class Meta:
        model = Help
        fields = ['limit_date', 'amount_expected', 'comments', 'member_id','administrator_id','member']

    def get_collected_amount(self, obj):
        return obj.calculate_help_amount()

class Obligatory_ContributionSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur

    class Meta:
        model = ObligatoryContribution
        fields = '__all__'

class BorrowingSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur

    class Meta:
        model = Borrowing
        fields = ['amount_borrowed','member_id','administrator_id','session_id','member']

class EpargneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Epargne
        fields = '__all__'

    def get_fond_social_percentage(self, obj):
        return obj.calculate_tresorerie_percentage()

class RefundSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur
    borrowing=BorrowingSerializer(source='borrowing_id', read_only=True)
    class Meta:
        model = Refund
        fields = '__all__'