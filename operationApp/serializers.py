from rest_framework import serializers

from members.serializers import MemberSerializer
from .models import *


class HelpTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpType
        fields = '__all__'
class HelpSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur
    helptype=HelpTypeSerializer(source='help_type_id', read_only=True) # Sérialiseur pour inclure l'util
    class Meta:
        model = Help
        fields = [ 'help_type_id','amount_expected', 'member_id','administrator_id','member','id','state','helptype']

    def get_collected_amount(self, obj):
        return obj.calculate_help_amount()       

class ContributionSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure les infos du membre
    help = HelpSerializer(source='help_id', read_only=True)  # Sérialiseur pour inclure l'aide


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


class PersonalContributionSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur
    help = HelpSerializer(source='help_id', read_only=True)  # Sérialiseur pour inclure l'aide


    class Meta:
        model = PersonalContribution
        fields = '__all__'

class Obligatory_ContributionSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur

    class Meta:
        model = ObligatoryContribution
        fields = '__all__'


class BorrowingSerializer(serializers.ModelSerializer):
    administrator = serializers.PrimaryKeyRelatedField(
        queryset=Administrator.objects.all(), 
        source='administrator_id',
        required=True
    )
    session = serializers.PrimaryKeyRelatedField(
        queryset=Session.objects.all(), 
        source='session_id',
        required=True
    )
    
    member = MemberSerializer(source='member_id', read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            'id',
            'amount_borrowed',
            'member_id',
            'administrator_id',
            'session_id',
            'exercise_id',
            'member',
            'session',
            'administrator',
            'amount_paid',
            'amount_to_pay',
            'payment_date_line',
            'create_at',
            'state',
            'late',
            'interest_rate',
            'interest_distribution'
        ]
        extra_kwargs = {
            'amount_paid': {'read_only': True},
            'amount_to_pay': {'read_only': True},
            'payment_date_line': {'read_only': True},
            'member': {'read_only': True},
            'create_at': {'read_only': True},
            'state': {'read_only': True},
            'late': {'read_only': True},
            'interest_distribution': {'read_only': True},
            'member_id': {'required': True},
            'administrator_id': {'required': True},
            'session_id': {'required': True},
            'exercise_id': {'required': True},
            'amount_borrowed': {'required': True}
        }

    def validate_amount_borrowed(self, value):
        """Validation du montant emprunté"""
        if value <= 0:
            raise serializers.ValidationError("Le montant emprunté doit être positif")
        return value

    def create(self, validated_data):
        try:
            # On initialise les champs obligatoires qui ne sont pas fournis
            validated_data['payment_date_line'] = timezone.now() + timedelta(days=30)
            
            # Calcul du montant à payer (principal + intérêts)
            amount_borrowed = Decimal(str(validated_data['amount_borrowed']))
            interest_rate = Decimal('3.00')  # Taux par défaut de 3%
            interest_amount = (amount_borrowed * interest_rate) / Decimal('100')
            validated_data['amount_to_pay'] = amount_borrowed + interest_amount
            
            # Création de l'emprunt
            borrowing = Borrowing.objects.create(**validated_data)
            return borrowing
            
        except Exception as e:
            raise serializers.ValidationError(f"REPONSE DU SERIALIZER : {str(e)}")

    def to_representation(self, instance):
        """Pour les GET, retourne la représentation complète"""
        representation = super().to_representation(instance)
        return representation

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