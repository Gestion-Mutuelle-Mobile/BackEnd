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

class Obligatory_ContributionSerializer(serializers.ModelSerializer):
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur

    class Meta:
        model = ObligatoryContribution
        fields = '__all__'

class BorrowingSerializer(serializers.ModelSerializer):
   
    administrator = serializers.PrimaryKeyRelatedField(
        queryset=Administrator.objects.all(), 
        source='administrator_id'
    )
    session = serializers.PrimaryKeyRelatedField(
        queryset=Session.objects.all(), 
        source='session_id'
    )
    
    member = MemberSerializer(source='member_id', read_only=True)  # Sérialiseur pour inclure l'utilisateur
    


    class Meta:
        model = Borrowing
        fields = ['amount_borrowed','member_id','administrator_id','session_id','member','session','administrator','amount_paid','amount_to_pay','id', 'payment_date_line', 'create_at']

        extra_kwargs = {
            'amount_paid': {'read_only': True},
            'amount_to_pay': {'read_only': True}
            , 'payment_date_line':{'read_only': True}, 'create_at':{'read_only': True}
        }
        
    def to_representation(self, instance):
        """
        Modifie la représentation pour inclure amount_paid et amount_to_pay pour les GET.
        """
        representation = super().to_representation(instance)
        
        return representation
    
    

    def to_internal_value(self, data):
        """
        Modifie les données internes pour exclure amount_paid et amount_to_pay pour les POST/PUT/PATCH.
        """
        internal_value = super().to_internal_value(data)
        # Supprime amount_paid et amount_to_pay des données pour les opérations d'écriture
        internal_value.pop('amount_paid', None)
        internal_value.pop('amount_to_pay', None)
        internal_value.pop('payment_date_line', None)
        internal_value.pop('create_at', None)
        
        internal_value.pop('id', None)
        return internal_value
    
    def create(self, validated_data):
        member = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), 
        source='member_id',
        
        )
        # Explicitly handle related object creation
        member = validated_data.pop('member_id')
        administrator = validated_data.pop('administrator_id')
        session = validated_data.pop('session_id')

        borrowing = Borrowing.objects.create(
            member_id=member,
            administrator_id=administrator,
            session_id=session,
            **validated_data
        )
        return borrowing

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